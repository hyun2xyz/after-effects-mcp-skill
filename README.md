# After Effects MCP Skill

Codex·Claude Code 같은 에이전트가 Adobe After Effects 작업을 가장 가벼운 경로로 처리하도록 안내하는 스킬입니다. 요청마다 MCP 지침과 도구 목록을 모두 읽지 않습니다. 요청에 맞는 경로 하나를 골라 실행하고, 지원하지 않거나 실패할 때만 다음 단계로 넘어갑니다.

| 순서 | 경로 | 쓰는 경우 |
|---|---|---|
| 1 | `laya-ae` 고정 명령 | 컴프 생성, 배경색, 텍스트·널·솔리드 추가, 선택 레이어 변형 같은 기본 조작 |
| 2 | `ae_basic.py` 배치 | 기본 조작 여러 개를 한 번에 |
| 3 | `scripts/run_jsx.py` | 고정 명령에 없지만 스크립트로 되는 작업을 요청별 JSX 한 번으로 실행 |
| 4 | 컴퓨터 유즈 | 플러그인 패널·대화상자·환경설정처럼 스크립트로 안 되는 UI, 화면 확인 |
| 5 | MCP·브리지 | MCP를 지정했거나 MCP 설치·연결 진단을 요청한 경우에만 사용 |

## 포함 파일

- [`skills/after-effects-mcp/SKILL.md`](skills/after-effects-mcp/SKILL.md): 경로 선택 규칙. 매번 읽는 부분이므로 짧게 유지합니다.
- [`skills/after-effects-mcp/scripts/run_jsx.py`](skills/after-effects-mcp/scripts/run_jsx.py): JSX 함수 본문을 After Effects에 한 번 보내고 짧은 JSON 결과를 출력합니다. macOS는 `DoScriptFile`, Windows는 `AfterFX.exe -r`을 사용하며 MCP 서버나 브리지 패널이 필요 없습니다.
- [`skills/after-effects-mcp/references/mcp-setup.md`](skills/after-effects-mcp/references/mcp-setup.md): MCP 설치·진단 절차. 5단계에서만 읽습니다.
- [`skills/after-effects-mcp/references/animation-checks.md`](skills/after-effects-mcp/references/animation-checks.md): 바닥 접촉 애니메이션 검수 규칙.

이 파일들은 `codex-harness-sync` 정본의 `skills/after-effects-mcp`를 복사한 스냅샷입니다. 원문에 나오는 `/Users/han/...` 경로는 작성자의 Mac 예시이므로 다른 환경에서는 실제 설치 경로를 확인해야 합니다. 1–2단계의 `laya-ae`는 [AFTEREFFECT_LAYA](https://github.com/hyun2xyz/AFTEREFFECT_LAYA)(`ae-basic-laya` 스킬)에 들어 있습니다. 설치하지 않았다면 3단계부터 사용합니다. 표현식 전용 `hi-lo` 스킬은 포함되어 있지 않습니다.

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

## 3단계 실행기 사용

```sh
python3 skills/after-effects-mcp/scripts/run_jsx.py --description "Read AE version" --code 'return app.version;'
python3 skills/after-effects-mcp/scripts/run_jsx.py --description "Add glow to selected layers" --undo /absolute/task.jsx
python3 skills/after-effects-mcp/scripts/run_jsx.py --description "Preview only" --code 'return 1;' --dry-run
```

- After Effects가 실행 중이어야 합니다. 설치된 AE가 여러 버전이면 `--app` 또는 `AE_APP`으로 하나를 지정합니다.
- 결과 파일을 쓰려면 AE 환경설정의 "스크립트가 파일을 쓰고 네트워크에 액세스하도록 허용"이 켜져 있어야 합니다. 이 설정은 파일 쓰기와 네트워크 접근을 함께 허용합니다.
- macOS에서는 처음 실행할 때 터미널이나 에이전트 앱의 After Effects 자동화 권한을 묻는 창이 뜰 수 있습니다.
- 시간 초과나 결과 없음(`unknown`)은 AE 대화상자 때문일 수 있습니다. 같은 명령을 다시 보내지 말고 AE 화면을 확인합니다.
- macOS AE 2026(26.5)에서 확인했습니다. Windows 실행은 아직 실제 기기에서 검증하지 않았습니다.

## 사용 범위

- 기본 조작은 `laya-ae`, 그 밖의 스크립트 작업은 요청별 JSX 한 번, UI 전용 단계는 컴퓨터 유즈로 처리
- 기존 MCP 서버, 브리지와 After Effects 인스턴스 확인 및 계층별 문제 진단(요청한 경우)
- 프로젝트 저장, 렌더링, 가져오기, 삭제와 덮어쓰기는 요청 범위를 확인합니다. 열려 있는 저장 전 프로젝트는 보존합니다.
