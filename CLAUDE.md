# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a **documentation and educational repository** about CrewAI, not an implemented project. It contains comprehensive Chinese language documentation about CrewAI framework concepts and implementation patterns.

## Current State

**Missing Implementation Files:**
- No Python source code files
- No package.json, requirements.txt, or pyproject.toml
- No configuration files (agents.yaml, tasks.yaml)
- No main entry point or build scripts

**Available Files:**
- `CrewAI_note.txt` - 418-line Chinese tutorial on CrewAI concepts
- `.claude/settings.local.json` - Claude Code permissions configuration

## Technology Stack (Referenced in Documentation)

- **Framework**: CrewAI - Python-based multi-agent AI framework
- **Language**: Python
- **AI Integration**: OpenAI API for LLM capabilities
- **Tools Package**: crewai[tools] with SerperDevTool, ScrapeWebsiteTool, etc.

## Architecture Patterns

The documentation describes CrewAI's core concepts:

1. **Agents**: Specialized AI roles with specific goals and backstories
2. **Tasks**: Well-defined work units with clear expected outputs
3. **Crews**: Teams of agents working collaboratively
4. **Flows**: Event-driven workflows with conditional logic

## To Make This a Functional CrewAI Project

The documentation suggests implementing a stock analysis system. To make this functional:

1. **Basic Structure Setup**:
   ```bash
   mkdir src config
   ```

2. **Dependencies**: Create `requirements.txt` with:
   ```
   crewai
   crewai[tools]
   openai
   python-dotenv
   ```

3. **Configuration Files**: Create `config/agents.yaml` and `config/tasks.yaml`

4. **Main Entry Point**: Create `src/main.py` with crew setup and execution

5. **Environment Setup**: Create `.env` file for API keys

## Development Guidelines (From Documentation)

- **Agent Design**: Single responsibility, clear goals, rich backstories
- **Task Decomposition**: Atomic tasks with clear dependencies
- **Tool Selection**: Role-appropriate tool assignment
- **Error Handling**: Retry mechanisms and monitoring
- **Performance**: Optimize agent count and use parallel processing

## Notes

This repository appears to be intended as a learning resource or starting point for CrewAI development. The extensive Chinese documentation covers theoretical concepts and implementation patterns but lacks the actual Python implementation files needed to run a CrewAI application.