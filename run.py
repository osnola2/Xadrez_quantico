import uvicorn

if __name__ == "__main__":
    print("🚀 Iniciando Servidor Xadrez Quântico e Simultâneo...")
    print("👉 Acesse no navegador: http://localhost:8000")
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)
