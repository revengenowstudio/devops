mkdir fetch_file
cd fetch_file
git init
git remote add origin "$REMOTE_GIT_URL"
git config core.sparseCheckout true
echo "修改归档*.md" >> .git/info/sparse-checkout
git fetch --depth=1 origin
git checkout FETCH_HEAD
cd ..