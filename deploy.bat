@echo off
echo === Pulling latest ===
git pull
echo.
echo === Deploying to Netlify ===
netlify deploy --prod --dir=.
echo.
echo === Submitting changed URLs to IndexNow ===
python scripts\indexnow_submit_changed.py
echo.
echo === Done ===
pause
