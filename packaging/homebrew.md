# Homebrew 유지보수

유지관리자의 PC에 Mac, Homebrew, PowerShell 작업 환경을 준비할 필요가 없습니다.
정식 릴리스를 게시하면 **macOS runner 하나가 체크섬 검증, Cask 갱신, 설치·제거 검사,
갱신 PR 생성까지 처리**합니다. 유지관리자는 결과와 변경 내용을 확인한 뒤 PR을 병합합니다.

## 최초 설정

1. 이 변경을 저장소 기본 브랜치에 병합합니다.
2. GitHub 저장소의 **Settings → Actions → General → Workflow permissions**에서
   **Allow GitHub Actions to create and approve pull requests**를 활성화합니다.
   이 workflow는 PR 생성만 사용하며, PR 승인이나 자동 병합은 하지 않습니다.
3. Actions가 활성화돼 있는지 확인합니다. 별도 PAT나 Apple Developer 계정은 필요하지 않습니다.

`GITHUB_TOKEN`의 `contents: write`, `pull-requests: write` 권한으로 저장소 안에
갱신 브랜치와 PR을 만듭니다. 일반 기여 PR의 검사는 읽기 권한만 사용하는 별도 workflow입니다.
조직 정책으로 PR 생성 설정이 잠겨 있다면 조직 관리자에게 해당 정책을 확인해야 합니다.

공개 저장소의 표준 `macos-latest` runner 실행은 무료입니다. 비공개 저장소는 요금제의
포함 사용량과 초과 요금이 적용되며, larger runner는 공개 저장소에서도 유료입니다.
[GitHub 공식 과금 문서](https://docs.github.com/en/billing/concepts/product-billing/github-actions)를 참고하세요.

## 정식 릴리스 이후 자동 처리

기존 방식대로 `v0.2.4` 같은 정식 버전 태그를 게시합니다.
[release.yml](../.github/workflows/release.yml)의 기존 폰트 빌드와 ZIP 게시가 성공하면,
마지막 job이 [update-homebrew.yml](../.github/workflows/update-homebrew.yml)을 직접 호출합니다.
토큰으로 게시한 릴리스 이벤트가 다른 workflow를 실행해 줄 것이라고 가정하지 않습니다.
사전 릴리스 태그와 릴리스 workflow의 수동 빌드에는 자동 갱신을 연결하지 않습니다.

macOS job은 다음 순서로 실행됩니다.

1. 게시된 릴리스의 Desktop ZIP, Desktop Nerd ZIP, `SHA256SUMS.txt`를 받습니다.
2. 실제 SHA-256과 공식 체크섬을 대조하고, ZIP 무결성과 TTF 14개 경로를 확인합니다.
3. 두 Cask의 버전·체크섬·다운로드 출처를 함께 갱신합니다.
4. **갱신한 파일 그대로** 임시 tap에 복사해 `brew style`, 두 패키지 설치,
   TTF 28개 존재 여부, 제거 후 파일 정리를 검사합니다.
5. 변경이 있으면 `automation/homebrew-<버전>` 브랜치의 PR을 생성하거나 갱신합니다.
   이미 같은 Cask라면 검사만 수행하고 PR은 추가하지 않습니다.

체크섬 불일치, ZIP 손상, TTF 구성 변경, 버전 역행, 설치·제거 검사 실패 시
새 갱신 내용을 PR로 게시하지 않습니다. 파일명이나 패밀리 구조가 바뀐 릴리스는
자동으로 추측하지 않으며, Cask와 검사 스크립트를 검토해야 합니다.

PR 본문에 연결된 Actions 실행이 성공했는지 확인하고 `Casks/` 변경만 검토해 병합합니다.
자동 PR에서 추가 검사가 승인 대기로 표시되면 **Approve workflows to run**으로 실행합니다.
PR 생성 전에 수행한 설치·제거 검사는 해당 실행 링크에서 확인할 수 있습니다.

## 수동 재실행과 fork 시험

GitHub의 **Actions → Update Homebrew → Run workflow**에서 실행합니다.

- **Branch**: Cask를 읽고 갱신 PR의 대상으로 삼을 브랜치입니다. 일반 운영에서는 `main`을 선택합니다.
- **tag**: 게시된 정식 태그입니다. 비워 두면 최신 정식 릴리스를 사용합니다.
- **source_repository**: 일반 운영에서는 비워 둡니다. 현재 저장소의 릴리스를 사용합니다.
  릴리스 자산이 없는 fork에서 시험할 때만 `younjungpark/Monatendard`를 입력합니다.

fork에서도 위 최초 설정이 필요합니다. workflow 파일은 fork의 기본 브랜치에 먼저 있어야 합니다.
fork 시험은 원본 저장소에 PR을 보내거나 릴리스를 게시하지 않습니다.
업데이트 성공 경로를 시험하려면 fork의 별도 시험 브랜치에서 Cask를 이전 정식 버전으로
준비한 후 최신 릴리스로 실행합니다. 이전 버전의 체크섬도 해당 공식 ZIP과 일치시킵니다.
생성된 PR의 대상이 시험 브랜치인지 확인하고, 시험용 이전 버전 변경은 원본 제출에 포함하지 않습니다.

## 실패했을 때

**Actions → Update Homebrew** 또는 **Release → update-homebrew**에서 실패한 단계의 로그를 확인합니다.

| 실패 단계 | 확인할 내용 |
|---|---|
| 다운로드 | 릴리스가 정식으로 게시됐는지, ZIP 두 개와 SHA256SUMS.txt가 있는지 |
| 체크섬·경로 검증 | 릴리스 파일 교체 여부, TTF 이름이나 구성 변경 여부 |
| 설치·제거 검사 | Homebrew 오류와 변경된 폰트 경로 |
| PR 생성 | Actions의 PR 생성 허용 설정, 조직 정책, 브랜치 보호 규칙 |

실패 원인을 수정한 뒤 같은 버전으로 다시 실행합니다. 검사를 피하기 위해
체크섬을 생략하거나 설치 실패를 성공으로 처리하지 않습니다.

## 사용자 설치와 업그레이드

이 저장소의 `Casks/`가 Homebrew tap 역할을 합니다. 별도 Homebrew 등록 승인은 필요하지 않습니다.
원본 저장소에 변경이 병합된 뒤 사용자는 macOS에서 아래 명령을 실행합니다.

```sh
brew tap younjungpark/monatendard https://github.com/younjungpark/Monatendard.git
brew install --cask younjungpark/monatendard/font-monatendard
brew install --cask younjungpark/monatendard/font-monatendard-nerd-font

brew update
brew upgrade --cask younjungpark/monatendard/font-monatendard younjungpark/monatendard/font-monatendard-nerd-font
```

필요한 패키지만 설치하면 됩니다. 각 패키지는 TTF 14개를 설치하며 두 패밀리는 공존합니다.
`brew update`가 병합된 Cask 정의를 가져오고 `brew upgrade`가 설치된 이전 버전을 교체합니다.
`livecheck`는 최신 정식 버전 조회 기능이고, 실제 파일 갱신은 위 Actions가 담당합니다.

## 검사 범위

자동 검사는 ZIP·체크섬·TTF 구성, Cask 스타일, 신규 설치와 제거를 확인합니다.
이전 버전에서의 실제 업그레이드와 IDE·터미널 화면 렌더링은 포함하지 않습니다.
패밀리명·파일명·폰트 구조가 바뀌면 macOS 사용자에게 해당 확인을 요청합니다.

0.2.3은 별도로 로컬 macOS CoreText에서 28개 폰트 로딩, PostScript 이름 중복 없음,
영문·한글 1:2 폭, Nerd 아이콘 일부를 확인했습니다. 이는 모든 글리프와 앱의 표시를 보장하지 않습니다.
