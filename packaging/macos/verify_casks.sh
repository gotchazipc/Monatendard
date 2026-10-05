#!/usr/bin/env bash
# GitHub macOS runner 전용: 기존 Monatendard 설치가 없는 환경에서 실행합니다.
set -euo pipefail

tap="monatendard-ci/fonts"
font_dir="${RUNNER_TEMP:?}/monatendard-fonts"
casks=("$tap/font-monatendard" "$tap/font-monatendard-nerd-font")
for token in font-monatendard font-monatendard-nerd-font; do
  if brew list --cask "$token" >/dev/null 2>&1; then
    echo "기존 설치가 있어 검사를 중단합니다: $token" >&2
    exit 1
  fi
done

# checkout을 복제하면 미커밋 갱신이 빠진다. tap을 만든 뒤 검사할 파일을 직접 복사한다.
brew tap-new "$tap"
cleanup() {
  for cask in "${casks[@]}"; do
    if brew list --cask "$cask" >/dev/null 2>&1; then
      brew uninstall --cask "$cask" || true
    fi
  done
  brew untap "$tap"
}
trap cleanup EXIT
tap_dir="$(brew --repository "$tap")"
mkdir -p "$tap_dir/Casks" "$font_dir"
cp Casks/font-monatendard.rb Casks/font-monatendard-nerd-font.rb "$tap_dir/Casks/"
if brew help trust >/dev/null 2>&1; then
  brew trust --cask "${casks[@]}"
fi
brew style "$tap_dir/Casks/font-monatendard.rb" "$tap_dir/Casks/font-monatendard-nerd-font.rb"
brew install --cask --fontdir="$font_dir" "${casks[@]}"
for prefix in Monatendard MonatendardNFM; do
  for style in Bold BoldItalic ExtraBold ExtraBoldItalic ExtraLight ExtraLightItalic Italic Light LightItalic Medium MediumItalic Regular SemiBold SemiBoldItalic; do
    test -s "$font_dir/$prefix-$style.ttf"
  done
done
brew uninstall --cask "${casks[@]}"
test -z "$(find "$font_dir" -type f -name '*.ttf' -print)"
echo "PASS: 두 Cask 스타일·설치·TTF 28개·제거 검사 완료"
