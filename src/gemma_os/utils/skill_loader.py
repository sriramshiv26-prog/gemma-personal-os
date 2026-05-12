"""SKILL.md loader - Load portable domain expertise"""

import os
from pathlib import Path
from typing import Dict, Optional, List


class SkillLoader:
    """Load SKILL.md files from skills directory"""

    def __init__(self, skill_dir: Optional[str] = None):
        """Initialize skill loader

        Args:
            skill_dir: Directory containing SKILL.md files (default: ~/.gemma-os/skills/)
        """
        if skill_dir:
            self.skill_dir = Path(skill_dir)
        else:
            self.skill_dir = Path.home() / ".gemma-os" / "skills"

        self.skills = {}

    def load_skill(self, skill_name: str) -> Optional[Dict]:
        """Load a single SKILL.md file

        Args:
            skill_name: Name of the skill (e.g., 'security-auditing')

        Returns:
            Dict with skill metadata and content, or None if not found
        """
        skill_path = self.skill_dir / skill_name / "SKILL.md"

        if not skill_path.exists():
            print(f"⚠ Skill not found: {skill_path}")
            return None

        try:
            with open(skill_path, 'r', encoding='utf-8') as f:
                content = f.read()

            skill = {
                'name': skill_name,
                'path': str(skill_path),
                'content': content,
                'loaded_at': str(Path(skill_path).stat().st_mtime),
            }

            # Parse metadata from frontmatter
            if content.startswith('---'):
                lines = content.split('\n')
                in_frontmatter = False
                for i, line in enumerate(lines):
                    if line.strip() == '---':
                        if not in_frontmatter:
                            in_frontmatter = True
                        else:
                            break
                    elif in_frontmatter and ':' in line:
                        key, value = line.split(':', 1)
                        skill[key.strip()] = value.strip()

            self.skills[skill_name] = skill
            return skill

        except Exception as e:
            print(f"✗ Error loading skill {skill_name}: {e}")
            return None

    def load_all(self) -> Dict[str, Dict]:
        """Load all SKILL.md files from skills directory

        Returns:
            Dict of all loaded skills
        """
        if not self.skill_dir.exists():
            print(f"⚠ Skills directory not found: {self.skill_dir}")
            return {}

        skill_dirs = [d for d in self.skill_dir.iterdir() if d.is_dir()]

        for skill_dir in skill_dirs:
            skill_name = skill_dir.name
            self.load_skill(skill_name)

        print(f"✓ Loaded {len(self.skills)} skills")
        return self.skills

    def get_skill(self, skill_name: str) -> Optional[Dict]:
        """Get loaded skill by name"""
        return self.skills.get(skill_name)

    def list_skills(self) -> List[str]:
        """List all loaded skills"""
        return list(self.skills.keys())

    def get_skill_context(self, skill_name: str) -> str:
        """Get skill content for prompt injection

        Returns:
            The SKILL.md content for use as context in model prompt
        """
        skill = self.get_skill(skill_name)
        if skill:
            return skill.get('content', '')
        return ''
