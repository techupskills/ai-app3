# TechCorp Enterprise AI Workshop - Setup Troubleshooting

## Issue: Python packages not installed in Codespaces

If you see errors like "requests not installed" when running the environment verification, follow these steps:

### Quick Fix (Recommended)
```bash
# Run the manual installation script
chmod +x install_dependencies.sh
./install_dependencies.sh
```

### Alternative Fix
```bash
# Install packages manually
pip install -r requirements.txt
```

### Verify Installation
```bash
# Run the environment verification
./scripts/verify_environment.sh
```

## Expected Output After Fix
You should see:
```
📚 Checking Python dependencies...
Critical packages:
✅ requests (2.x.x)
✅ fastapi (0.x.x)
✅ uvicorn (0.x.x)
✅ streamlit (1.x.x)
... (all packages showing green checkmarks)
```

## If Problems Persist

1. **Check Python version**: `python3 --version` (should be 3.9+)
2. **Check pip**: `pip --version`
3. **Try individual package installation**:
   ```bash
   pip install requests fastapi uvicorn streamlit pandas numpy plotly pydantic httpx pyjwt chromadb
   ```

## GitHub Codespaces Specific Issues

- The devcontainer should automatically install dependencies
- If it doesn't work, the postCreateCommand might have failed
- Run the manual installation script as a workaround

## Contact
If you continue having issues, check the workshop instructor or repository issues.