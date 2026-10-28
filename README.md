# After Effects MCP Skill

Codex에서 Adobe After Effects와 MCP 연결을 진단하고, 요청받은 프로젝트 작업을 안전하게 수행하기 위한 스킬입니다.

이 저장소에는 스킬 지침이 들어 있습니다. **After Effects, MCP 서버, 브리지 패널이나 JSX 실행기는 포함되어 있지 않습니다.** 실제 연결에는 사용 중인 서버와 브리지를 별도로 설정해야 합니다. 스킬은 기존 구현을 확인한 다음 연결 상태를 단계별로 진단하도록 안내합니다.

## 포함 파일

- [`skills/after-effects-mcp/SKILL.md`](skills/after-effects-mcp/SKILL.md): 스킬 원문

이 파일은 `codex-harness-sync` 정본의 `skills/after-effects-mcp/SKILL.md`를 복사한 스냅샷입니다. 원문에 나오는 `/Users/han/...` 경로는 작성자의 Mac에 대한 예시이므로 다른 환경에서는 실제 설치 경로를 확인해야 합니다. 표현식 전용 작업을 위한 `hi-lo` 스킬은 이 저장소에 포함되어 있지 않습니다.

## 설치

macOS 또는 Linux에서 저장소를 복제한 뒤 다음 명령을 실행합니다. 같은 이름의 스킬이 이미 있으면 덮어쓰지 않습니다.

```sh
git clone https://github.com/hyun2xyz/after-effects-mcp-skill.git
cd after-effects-mcp-skill
mkdir -p "$HOME/.agents/skills"
skill_target="$HOME/.agents/skills/after-effects-mcp"
if [ -e "$skill_target" ] || [ -L "$skill_target" ]; then
  echo "이미 설치된 스킬이 있습니다. 기존 파일을 확인하세요: $skill_target"
else
  cp -R skills/after-effects-mcp "$skill_target"
fi
```

새 Codex 세션에서 `after-effects-mcp` 스킬을 지정하거나 After Effects MCP 연결 진단을 요청합니다. 설치만으로 MCP 서버가 등록되거나 실행되지는 않습니다.

## 사용 범위

- 기존 MCP 서버, 브리지와 After Effects 인스턴스 확인
- 읽기 전용 연결 확인과 계층별 문제 진단
- 사용자가 요청한 범위의 After Effects 프로젝트 작업 및 결과 확인

프로젝트 저장, 렌더링, 가져오기, 삭제와 덮어쓰기는 요청 범위를 확인합니다. 열려 있는 저장 전 프로젝트는 보존합니다.
