# Remove everything from git tracking
git rm -r --cached .
# Add back only what you want
git add decode_morse.py README.md requirements.txt test_samples.md .gitignore
git add samples/*.flac samples/*.mp3
git commit -m "Clean commit: only source code and samples"
git push origin main