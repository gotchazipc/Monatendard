# Monatendard

Monatendard는 **Monaspace Neon의 영문과 Pretendard의 한글을 결합하고**,
한글 한 글자가 영문 두 글자의 너비와 정확히 맞도록 조정한 재현 가능한 코딩
글꼴 프로젝트입니다.

공식 소개·체험·다운로드: [monatendard.github.io](https://monatendard.github.io/)

## Monaspace Neon Frozen 원본과 비교

`윤곽`은 화면에 실제로 그려지는 글자 모양이고, `셀 너비`는 다음 글자가
시작될 때까지 확보되는 고정폭 공간입니다.

| 항목 | Monaspace Neon Frozen 원본 | Monatendard |
|---|---:|---:|
| 기준 좌표계 | `2000 units` | `2000 units` |
| 영문 셀 너비 | `1240`, `0.620em` | `1200`, `0.600em` |
| 일반 영문 윤곽 가로 배율 | 100% | 92.5% |
| 영문 세로 배율 | 100% | 100% |
| 한글·CJK 윤곽 배율 | 없음 | 최대 가로 113%, 세로 111% |
| 한글 셀 너비 | 없음 | `2400`, 영문 두 글자의 너비 |

일반 사용자는 공식 사이트의 `Monatendard-v*-Desktop.zip`만 내려받아 압축을 풀고
`Install-Monatendard.ps1`을 실행하면 됩니다. Python, uv, Make는 필요하지 않습니다.

Oh My Posh 같은 터미널 아이콘이 필요하면 일반판 대신
`Monatendard-v*-Desktop-Nerd.zip`을 설치하고 글꼴을
`Monatendard Nerd Font Mono`로 선택하세요. 일반판과 별도 패밀리라 함께 설치할 수 있습니다.

## 일반 사용자 설치

### Windows

1. [공식 사이트](https://monatendard.github.io/#download)의 Desktop ZIP을 내려받아 압축을 풉니다.
2. PowerShell에서 `Install-Monatendard.ps1`을 실행합니다.
3. 사용 중인 편집기나 터미널을 다시 시작하고 글꼴을 `Monatendard`로 선택합니다.
4. 제거할 때는 같은 폴더의 `Uninstall-Monatendard.ps1`을 실행합니다.

스크립트는 관리자 권한 없이 현재 사용자 영역에 설치합니다.

### macOS (Homebrew)

이 저장소를 Homebrew tap으로 추가한 다음, 필요한 패키지를 설치합니다.

```sh
brew tap younjungpark/monatendard https://github.com/younjungpark/Monatendard.git
# 일반판: 편집기와 일반 애플리케이션용
brew install --cask younjungpark/monatendard/font-monatendard
# Nerd판: 아이콘을 사용하는 터미널용
brew install --cask younjungpark/monatendard/font-monatendard-nerd-font
```

각 패키지는 공식 릴리스의 TTF 14종을 `~/Library/Fonts`에 설치합니다.
폰트 빌드나 PowerShell 실행은 필요하지 않습니다. 두 패밀리는 함께 설치할 수 있습니다.
편집기나 터미널을 다시 시작하고 `Monatendard` 또는 `Monatendard Nerd Font Mono`를 선택하세요.

업그레이드와 제거는 다음 명령을 사용합니다. 하나만 설치했다면 해당 패키지 이름만 지정합니다.

```sh
brew update
brew upgrade --cask younjungpark/monatendard/font-monatendard younjungpark/monatendard/font-monatendard-nerd-font
brew uninstall --cask younjungpark/monatendard/font-monatendard younjungpark/monatendard/font-monatendard-nerd-font
```

정식 릴리스 후 macOS Actions가 Cask 갱신·검증 PR을 만듭니다.
해당 PR이 병합되면 Homebrew에서도 업그레이드할 수 있습니다.
유지보수 절차는 [homebrew.md](packaging/homebrew.md)를 참고하세요.

## 개발자 빌드

필요 조건은 Python 3.11 이상과 [uv](https://docs.astral.sh/uv/)입니다.

```powershell
uv sync --all-groups
uv run monatendard fetch
uv run monatendard build --variants Regular
uv run monatendard verify
uv run monatendard build-nerd --variants Regular
uv run monatendard verify --nerd
```

전체 14개 weight/style 조합은 다음 명령으로 빌드합니다.

```powershell
uv run monatendard build --all
uv run monatendard build-nerd --all
```

생성 파일은 `fonts/ttf`, `fonts/nerd-ttf`, `fonts/webfont`에 저장되며
Git에는 포함되지 않습니다.
원본 아카이브도 `upstream/` 아래에만 저장되고 Git에서 제외됩니다.

### Monatendard 생성 과정

1. Monaspace Neon Frozen, Pretendard, Nerd Fonts 원본 버전을 고정하고 SHA256을 확인합니다.
2. Monaspace 글리프 윤곽을 가로 92.5%로 조정하고 0.600em 영문 셀 안에 배치하되,
   박스 드로잉·블록·Powerline 문자는 셀 경계가 이어지도록 맞춥니다. 이탤릭에서도
   연결 문자는 같은 굵기의 upright 윤곽을 사용합니다.
3. Pretendard 한글·CJK 글리프를 가로 113%, 세로 111%로 조정해 영문 두 칸 셀에 병합합니다.
4. Monatendard 패밀리명, 스타일, 고정폭, 버전 및 라이선스 정보를 설정합니다.
5. 데스크톱용 TTF, 웹용 WOFF2 및 `@font-face` CSS를 생성합니다.
6. 선택적으로 Nerd Fonts Symbols Only 아이콘을 영문 한 칸 너비로 병합합니다.
7. 글리프 범위, 셀 너비, 리게이처, 글꼴 정보와 빌드 재현성을 검증한 뒤 패키징합니다.

## 명령

- `monatendard fetch`: 잠금 파일의 URL에서 원본을 받고 SHA256을 확인합니다.
- `monatendard build`: 영문 윤곽·셀 변환과 Pretendard 글리프 병합을 수행합니다.
- `monatendard build-nerd`: 일반판에 고정된 Nerd Fonts Symbols Only 아이콘을 병합합니다.
- `monatendard verify`: 이름, 폭, 한글 글리프, 리게이처, 테이블 무결성을 확인합니다.
- `monatendard verify --nerd`: Nerd 패밀리명, 필수 아이콘과 한 칸 폭을 추가 검사합니다.
- `monatendard package --version 0.2.3`: Desktop/Desktop-Nerd/Web ZIP과 체크섬을 만듭니다.

`Makefile`은 개발자용 단축 명령일 뿐이며 사용자 설치 과정에는 필요하지 않습니다.

## 고정 버전

| 항목 | 값 |
|---|---|
| Monatendard | 0.2.3 |
| Monaspace Neon | 1.400 |
| Pretendard | 1.3.9 |
| Nerd Fonts Symbols Only | 3.4.0 |

원본 URL과 아카이브 SHA256은 `sources.lock.toml`이 유일한 기준입니다. 같은 잠금 파일과
도구 버전으로 만든 결과의 바이트 재현성도 테스트합니다.

## 저장소 운영

- `main`에는 빌드 코드, 테스트, 문서, 워크플로만 둡니다.
- 원본 폰트, 생성 폰트, `dist/`는 커밋하지 않습니다.
- 버전은 SemVer 태그로 관리합니다. 하이픈이 있는 태그는 GitHub 사전 릴리스가 됩니다.
- Release workflow는 고정 원본 검증, 전체 빌드, 자동 테스트, 패키징, 체크섬 검증 후
  GitHub Release 자산을 게시합니다.

## 라이선스

Monaspace와 Pretendard는 SIL Open Font License 1.1로, Nerd Fonts Symbols Only는
MIT License로 배포됩니다. Monatendard는 원본의 Reserved Font Name을 사용하지 않는
별도 패밀리 이름입니다. 자세한 저작권과 고지는 `licenses/`를 확인해 주세요.
