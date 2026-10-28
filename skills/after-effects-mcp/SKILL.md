---
name: after-effects-mcp
description: "AE work router: laya-ae fixed commands, one-shot JSX via run_jsx.py, computer use for UI-only steps; MCP only for setup, diagnosis, or explicit requests. Expressions: hi-lo."
---

# After Effects 작업 라우터

MCP 지침·도구를 매번 읽지 않는다. 처리 가능한 가장 가벼운 경로로 실행하고, 지원하지 않거나 실패할 때만 다음 단계로 간다. 표현식만 다루면 `hi-lo`.

| 순서 | 경로 | 쓰는 경우 |
|---|---|---|
| 1 | `laya-ae` 고정 명령 | 컴프 생성, 배경색, 텍스트·널·솔리드, 선택 레이어 이름·변형·표시, 불투명도 2점 키, 현재 상태 |
| 2 | `ae_basic.py` 배치 | 1단계 조작 여러 개 |
| 3 | `scripts/run_jsx.py` | 고정 명령 밖이지만 스크립트로 되는 작업(이펙트, 마커, 프리컴프, 표현식 적용, 렌더 큐 추가, 조회) |
| 4 | 컴퓨터 유즈 | 스크립트 API 없는 UI(플러그인 패널, 대화상자, 환경설정), 화면 확인, 대화상자에 막힌 3단계 |
| 5 | MCP·브리지 | MCP 지정·설치·진단 요청 때만 [MCP 설치·진단](references/mcp-setup.md)을 읽는다 |

한 요청도 나눈다. 예: 값 설정은 3단계, 플러그인 UI만 4단계.

## 1–2단계: laya-ae

- `ae-basic-laya`([AFTEREFFECT_LAYA](https://github.com/hyun2xyz/AFTEREFFECT_LAYA))의 명령이다. `command -v laya-ae`가 없으면 설치하지 말고 3단계로 간다.
- 애매하면 `--dry-run`으로 해석만 보고 한 번 실행한다. 문형은 `laya-ae --list`, 배치는 `ae-basic-laya` commands.md의 배치 부분만 본다.
- `unsupported`·파싱 실패는 3단계로. `partial`·timeout·receipt 누락은 재전송하지 말고 상태부터 읽는다. 출력은 요약만 읽는다.

## 3단계: 요청별 JSX 한 번

필요한 JSX 함수 본문만 쓰고 한 번 보낸다. MCP·브리지 패널 없이 Mac `DoScriptFile`, Windows `AfterFX.exe -r`로 실행한다.

```sh
python3 scripts/run_jsx.py --description "Read AE version" --code 'return app.version;'
python3 scripts/run_jsx.py --description "Add glow to selected layers" --undo /absolute/task.jsx
```

- `return {…}`으로 이름·ID·개수 같은 짧은 요약만 돌려준다. 상태를 모르면 필요한 값만 먼저 읽고, 변경은 한 본문에 묶는다.
- 변경에는 `--undo`. 대상 컴프·레이어가 없거나 여럿이면 추측하지 말고 `throw`한다.
- `error`는 `body line`을 보고 고쳐 다시 보낸다. `unknown`(timeout·결과 없음)은 재전송하지 말고 4단계로 대화상자를 확인한다.
- 결과 파일에는 AE의 "스크립트가 파일을 쓰고 네트워크에 액세스하도록 허용"이 필요하다. 꺼져 있으면 영향을 설명하고 사용자가 켜게 한다. AE가 여러 버전이면 `--app`.

## 4단계: 컴퓨터 유즈

- 스크립트로 되는 일을 클릭으로 대신하지 않는다. AE 창만 `app_*` 도구로 다루고, 동작을 묶은 뒤 스크린샷은 한 번 찍는다.
- 저장·렌더·덮어쓰기·삭제 버튼과 권한·보안 설정은 명시 요청 없이 누르지 않는다. UI 작업 뒤 3단계 읽기 JSX로 값을 확인한다.

## 안전·검증·보고

- 저장 전 프로젝트를 닫거나 바꾸지 않는다. 저장·렌더·가져오기·삭제·덮어쓰기는 요청 범위와 명시 경로가 있을 때만 한다. 직접 쓰거나 확인한 JSX만 실행한다.
- 완료는 readback 값이나 프레임 한 장으로 확인한다. 종료 코드 0이나 `prepared`는 완료가 아니다. 바닥 접촉 애니메이션은 [접촉 검수](references/animation-checks.md)를 읽는다.
- 보고: 사용한 단계, 명령, readback 근거, 남은 수동 확인, AE에 남긴 상태.
