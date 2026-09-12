cask "font-monatendard-nerd-font" do
  version "0.2.2"
  sha256 "1fbf7cfb4a1a188ac17d65c7ffbee788e176decfd0ad04ed5646ece15d0475b9"

  url "https://github.com/younjungpark/Monatendard/releases/download/v#{version}/Monatendard-v#{version}-Desktop-Nerd.zip",
      verified: "github.com/younjungpark/Monatendard/"
  name "Monatendard Nerd Font Mono"
  desc "Monatendard with Nerd Font icons for terminals"
  homepage "https://monatendard.github.io/"

  livecheck do
    url :url
    strategy :github_latest
  end

  font "fonts/MonatendardNFM-Bold.ttf"
  font "fonts/MonatendardNFM-BoldItalic.ttf"
  font "fonts/MonatendardNFM-ExtraBold.ttf"
  font "fonts/MonatendardNFM-ExtraBoldItalic.ttf"
  font "fonts/MonatendardNFM-ExtraLight.ttf"
  font "fonts/MonatendardNFM-ExtraLightItalic.ttf"
  font "fonts/MonatendardNFM-Italic.ttf"
  font "fonts/MonatendardNFM-Light.ttf"
  font "fonts/MonatendardNFM-LightItalic.ttf"
  font "fonts/MonatendardNFM-Medium.ttf"
  font "fonts/MonatendardNFM-MediumItalic.ttf"
  font "fonts/MonatendardNFM-Regular.ttf"
  font "fonts/MonatendardNFM-SemiBold.ttf"
  font "fonts/MonatendardNFM-SemiBoldItalic.ttf"
end
