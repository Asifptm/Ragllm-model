@echo off
echo Testing RAG API with curl commands...
echo.

echo === HEALTH CHECK ===
curl -X GET http://localhost:8000/health
echo.
echo.

echo === CHAT API TEST ===
curl -X POST http://localhost:8000/chat ^
  -H "Content-Type: application/json" ^
  -d "{\"query\":\"What is Retrieval-Augmented Generation?\"}"
echo.
echo.

echo === WEBSOURCE API TEST ===
curl -X GET http://localhost:8000/websource
echo.
echo.

echo === RELATED API TEST ===
curl -X GET http://localhost:8000/related
echo.
echo.

echo === CUSTOM QUERY TEST ===
set /p custom_query="Enter your query: "
curl -X POST http://localhost:8000/chat ^
  -H "Content-Type: application/json" ^
  -d "{\"query\":\"%custom_query%\"}"
echo.
echo.

pause
