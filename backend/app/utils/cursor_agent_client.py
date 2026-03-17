"""
Cursor Agent CLI client
Invokes cursor-agent as the main brain for ontology, entity extraction, config, profiles, and reports.
"""

import json
import os
import re
import subprocess
import tempfile
from typing import Optional, Dict, Any, List

from ..config import Config
from ..utils.logger import get_logger

logger = get_logger('mirofish.cursor_agent')


class CursorAgentClient:
    """
    Client that invokes cursor-agent CLI for AI tasks.
    Replaces LLMClient/Ollama - uses Cursor Agent as the brain.
    """

    def __init__(
        self,
        agent_path: Optional[str] = None,
        workspace: Optional[str] = None,
        timeout: int = 300,
    ):
        self.agent_path = agent_path or Config.CURSOR_AGENT_PATH
        self.workspace = workspace or os.getcwd()
        self.timeout = timeout

    def chat(
        self,
        prompt: str,
        context_files: Optional[Dict[str, str]] = None,
        temperature: float = 0.7,
        max_tokens: int = 4096,
    ) -> str:
        """
        Send a prompt to Cursor Agent and return the response text.

        Args:
            prompt: The main prompt for the agent
            context_files: Optional dict of {filename: content} to write to workspace for context
            temperature: Unused (kept for API compatibility)
            max_tokens: Unused (kept for API compatibility)

        Returns:
            Agent response text
        """
        full_prompt = self._build_prompt(prompt, context_files)
        return self._invoke(full_prompt, expect_json=False)

    def chat_json(
        self,
        prompt: str,
        context_files: Optional[Dict[str, str]] = None,
        temperature: float = 0.3,
        max_tokens: int = 4096,
    ) -> Dict[str, Any]:
        """
        Send a prompt and parse the response as JSON.

        Args:
            prompt: The main prompt (should request valid JSON output)
            context_files: Optional dict of {filename: content} for context
            temperature: Unused (kept for API compatibility)
            max_tokens: Unused (kept for API compatibility)

        Returns:
            Parsed JSON object
        """
        json_instruction = (
            "\n\nRespond with valid JSON only. No markdown, no explanation, no code blocks. "
            "Output the raw JSON object."
        )
        full_prompt = self._build_prompt(prompt, context_files) if context_files else prompt
        full_prompt = full_prompt + json_instruction

        response = self._invoke(full_prompt, expect_json=False)
        return self._parse_json_response(response)

    def _build_prompt(self, prompt: str, context_files: Optional[Dict[str, str]]) -> str:
        """Build prompt with optional context files written to workspace."""
        if not context_files:
            return prompt

        written_paths = []
        for filename, content in context_files.items():
            path = os.path.join(self.workspace, filename)
            os.makedirs(os.path.dirname(path) or '.', exist_ok=True)
            with open(path, 'w', encoding='utf-8') as f:
                f.write(content)
            written_paths.append(path)

        paths_str = '\n'.join(f'- {p}' for p in written_paths)
        return f"{prompt}\n\nContext files (in workspace):\n{paths_str}\n\nUse these files for context."

    def _invoke(self, prompt: str, expect_json: bool = False) -> str:
        """Invoke cursor-agent and return the result."""
        cmd = [
            self.agent_path,
            '-p',
            prompt,
            '--output-format', 'json',
            '--trust',
            '--workspace', self.workspace,
        ]

        logger.debug(f"Invoking cursor-agent (workspace={self.workspace})")
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=self.timeout,
                cwd=self.workspace,
            )
        except subprocess.TimeoutExpired:
            raise TimeoutError(f"Cursor Agent timed out after {self.timeout}s")
        except FileNotFoundError:
            raise ValueError(
                f"cursor-agent not found at '{self.agent_path}'. "
                "Install or ensure it's in PATH: curl https://cursor.com/install -fsS | bash"
            ) from None

        if result.returncode != 0:
            raise RuntimeError(
                f"Cursor Agent failed (exit {result.returncode}): {result.stderr or result.stdout}"
            )

        # Parse JSON lines from stdout (cursor-agent may output multiple JSON objects)
        lines = (result.stdout or '').strip().split('\n')
        for line in reversed(lines):
            line = line.strip()
            if not line:
                continue
            try:
                obj = json.loads(line)
                if obj.get('type') == 'result' and obj.get('subtype') == 'success':
                    return (obj.get('result') or '').strip()
                if obj.get('is_error'):
                    raise RuntimeError(obj.get('result', 'Unknown error'))
            except json.JSONDecodeError:
                continue

        raise RuntimeError(f"No valid result from Cursor Agent: {result.stdout[:500]}")

    def _parse_json_response(self, response: str) -> Dict[str, Any]:
        """Parse response and extract JSON, stripping markdown code blocks and leading text."""
        cleaned = response.strip()

        # 1. Extract content from ```json ... ``` or ``` ... ``` block (anywhere in response)
        code_block = re.search(
            r'```(?:json)?\s*\n?(.*?)\n?```',
            cleaned,
            re.DOTALL | re.IGNORECASE,
        )
        if code_block:
            cleaned = code_block.group(1).strip()

        # 2. Fallback: strip markdown only if at start/end
        if not cleaned.startswith('{') and not cleaned.startswith('['):
            cleaned = re.sub(r'^```(?:json)?\s*\n?', '', cleaned, flags=re.IGNORECASE)
            cleaned = re.sub(r'\n?```\s*$', '', cleaned)
            cleaned = cleaned.strip()

        # 3. If still has leading text, try to find first { or [ and parse from there
        if not cleaned.startswith('{') and not cleaned.startswith('['):
            for start_char, end_char in [('{', '}'), ('[', ']')]:
                idx = cleaned.find(start_char)
                if idx >= 0:
                    depth = 0
                    for i in range(idx, len(cleaned)):
                        if cleaned[i] == start_char:
                            depth += 1
                        elif cleaned[i] == end_char:
                            depth -= 1
                            if depth == 0:
                                try:
                                    return json.loads(cleaned[idx : i + 1])
                                except json.JSONDecodeError:
                                    break
                    break

        try:
            return json.loads(cleaned)
        except json.JSONDecodeError:
            raise ValueError(f"Cursor Agent returned invalid JSON: {cleaned[:500]}")

    # Compatibility methods for services expecting LLMClient-style messages API
    def chat_json_messages(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.3,
        max_tokens: int = 4096,
    ) -> Dict[str, Any]:
        """
        Compatibility API: convert messages to prompt and return parsed JSON.
        """
        prompt_parts = []
        for m in messages:
            role = m.get('role', 'user')
            content = m.get('content', '')
            if role == 'system':
                prompt_parts.append(f"[System instructions - follow these exactly]\n{content}")
            elif role == 'user':
                prompt_parts.append(f"[User request]\n{content}")
            elif role == 'assistant':
                prompt_parts.append(f"[Previous response]\n{content}")
        prompt = '\n\n---\n\n'.join(prompt_parts)
        return self.chat_json(prompt, temperature=temperature)

    def chat_messages(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 4096,
        response_format: Optional[Dict] = None,
    ) -> str:
        """
        Compatibility API: convert messages to a single prompt and invoke.
        """
        prompt_parts = []
        for m in messages:
            role = m.get('role', 'user')
            content = m.get('content', '')
            if role == 'system':
                prompt_parts.append(f"[System: {content}]")
            elif role == 'user':
                prompt_parts.append(content)
            elif role == 'assistant':
                prompt_parts.append(f"[Previous response: {content}]")
        prompt = '\n\n'.join(prompt_parts)
        if response_format and response_format.get('type') == 'json_object':
            return json.dumps(self.chat_json(prompt, temperature=temperature))
        return self.chat(prompt, temperature=temperature)
