from fastapi import FastAPI
from pydantic import BaseModel
from app.agents.graphs.GraphBuilder import finalyser_graph

app = FastAPI()


class QueryRequest(BaseModel):
    query: str


@app.post("/query/")
async def query_graph(request: QueryRequest):
    inputs = {"messages": [("user", request.query)]}
    
    results = []
    for output in finalyser_graph.stream(inputs):
        results.append(output)
    
    return {"response": results}
