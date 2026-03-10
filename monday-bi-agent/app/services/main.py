from __future__ import annotations

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.models import ChatRequest, ChatResponse
from app.services.answer_writer import write_answer
from app.services.metrics import build_metrics_package
from app.services.monday_client import MondayAPIError, MondayClient
from app.services.normalizer import normalize_all
from app.services.query_router import route_query

app = FastAPI(title="Monday BI Agent", version="1.0.0")
app.mount("/static", StaticFiles(directory="app/static"), name="static")


@app.get("/")
def root():
    return FileResponse("app/static/index.html")


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/api/chat", response_model=ChatResponse)
def chat(req: ChatRequest):
    question = req.question.strip()
    if not question:
        raise HTTPException(status_code=400, detail="Question cannot be empty.")

    try:
        routed = route_query(question)

        if routed.needs_clarification:
            return ChatResponse(
                answer=routed.clarification_question or "Could you clarify your request?",
                diagnostics={"routed_query": routed.model_dump()}
            )

        monday = MondayClient()
        deals_board, work_orders_board = monday.fetch_deals_and_work_orders()

        deals_df, work_orders_df, caveats = normalize_all(deals_board, work_orders_board)

        metrics_package = build_metrics_package(
            question=question,
            routed_query=routed,
            deals_df=deals_df,
            work_orders_df=work_orders_df,
            caveats=caveats,
        )

        answer = write_answer(question, metrics_package)

        return ChatResponse(
            answer=answer,
            diagnostics={
                "routed_query": routed.model_dump(),
                "deals_rows": len(deals_df),
                "work_orders_rows": len(work_orders_df),
                "caveat_count": len(caveats),
            },
        )

    except MondayAPIError as e:
        raise HTTPException(status_code=502, detail=f"monday API error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected server error: {str(e)}")