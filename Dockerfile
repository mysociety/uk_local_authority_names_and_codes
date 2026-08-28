FROM python:3.14-bookworm

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/
COPY --from=ruby:2.7.1-slim /usr/local/ /usr/local/
COPY --from=ruby:2.7.1-slim /usr/lib/x86_64-linux-gnu/libssl.so.1.1 \
    /usr/lib/x86_64-linux-gnu/libcrypto.so.1.1 \
    /usr/lib/x86_64-linux-gnu/

ENV WORKSPACE_NAME=uk_local_authority_names_and_codes
ENV UV_LINK_MODE=symlink
ENV PATH="/usr/local/bin:${PATH}"
ENV PATH="/workspaces/$WORKSPACE_NAME/.venv/bin:${PATH}"

RUN <<EOF

# add gh cli
curl -fsSL https://cli.github.com/packages/githubcli-archive-keyring.gpg | dd of=/usr/share/keyrings/githubcli-archive-keyring.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" | tee /etc/apt/sources.list.d/github-cli.list > /dev/null
apt-get update
apt-get install gh
gh extension install ajparsons/gh-fix-submodule-remote
apt-get install bash-completion
apt-get install -y gdal-bin libgdal-dev pkg-config build-essential

# download ltex
cd /tmp/
echo "Downloading ltex"
wget https://github.com/valentjn/ltex-ls/releases/download/15.2.0/ltex-ls-15.2.0-linux-x64.tar.gz
echo "Untarring"
mkdir /ltex
tar -xf ltex-ls-15.2.0-linux-x64.tar.gz -C /ltex
echo "Removing source"
rm ltex-ls-15.2.0-linux-x64.tar.gz
echo "Finished ltex download"


# get node and pyright
apt-get install npm -y
npm install -g pyright

# getfonts
mkdir /tmp/adodefont
cd /tmp/adodefont
mkdir -p ~/.fonts

wget https://github.com/adobe-fonts/source-code-pro/archive/2.030R-ro/1.050R-it.zip
unzip 1.050R-it.zip
cp source-code-pro-2.030R-ro-1.050R-it/OTF/*.otf ~/.fonts/

wget https://github.com/adobe-fonts/source-serif-pro/archive/2.000R.zip
unzip 2.000R.zip
cp source-serif-2.000R/OTF/*.otf ~/.fonts/

wget https://github.com/adobe-fonts/source-sans-pro/archive/2.020R-ro/1.075R-it.zip
unzip 1.075R-it.zip
cp source-sans-2.020R-ro-1.075R-it/OTF/*.otf ~/.fonts/

apt-get install fonts-lato -y

fc-cache -f -v

apt-get install rsync -y

EOF