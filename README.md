
# **Finanalyser: Financial Analysis Multi-Agent Research Tool**

## **Overview**
This project is a **multi-agent hierarchical financial analysis research tool** built using LangGraph. It demonstrates how **hierarchical multi-agent frameworks** can be implemented for financial data analysis, research, and prediction.

The system consists of **two primary nodes**:
1. **Data Fetch & Store Node**
2. **Q&A Node**

Each of these nodes contains specialized sub-nodes to handle different types of financial data.

---

## **System Architecture**

### **1. Data Fetch & Store Node**
This node is responsible for fetching financial data from different sources and storing them efficiently.

It consists of two sub-nodes:

#### **a. YFinance Fetching Node**
- Fetches financial data such as stock prices, earnings reports, and historical trends using the **YFinance API**.
- Stores the structured financial data in a **PostgreSQL database**.

#### **b. Financial Document Ingestion Node**
- Accepts financial documents like **balance sheets, income statements, and cash flow statements** in **PDF format**.
- Extracts relevant data and stores it in a **vector database (FAISS)** for efficient retrieval.

---

### **2. Q&A Node**
This node processes user queries by searching financial data across different sources.

It consists of three sub-nodes:

#### **a. Vector Search Node**
- Searches the **vector database** for relevant information from ingested financial PDFs.
- Uses **FAISS** to perform fast and efficient retrieval of stored document embeddings.

#### **b. PostgreSQL Query Node**
- Fetches financial data for a given company from the **PostgreSQL database**.
- Calls the **Pandas Agent** to analyze the retrieved data and generate responses.

#### **c. Web Scraper Node**
- Performs a **real-time web search** for additional financial data.
- Uses scraping APIs to extract relevant financial insights from the internet.

Each time a user asks a financial question, **all three sub-nodes** (Vector Search, PostgreSQL Query, Web Scraper) are executed, and the system returns results from each source.

---

## **Technology Stack**
- **Python** (Main backend development)
- **LangGraph** (Hierarchical multi-agent framework)
- **YFinance API** (Stock market data retrieval)
- **FAISS** (Vector store for efficient document retrieval)
- **PostgreSQL** (Relational database for structured financial data)
- **Web Scraping APIs** (For real-time financial data extraction)

---

## **How It Works**
1. **User requests financial data** → The system fetches data from YFinance and PostgreSQL.
2. **User uploads financial documents** → The system processes and stores them in a vector database.
3. **User asks a financial question** → The system retrieves relevant answers from:
   - Vector DB (PDFs)
   - PostgreSQL DB (Structured data + Pandas analysis)
   - Web Search (Real-time financial insights)

All three answers are returned, providing a **comprehensive financial analysis**.

---

This setup ensures that **financial insights are data-driven, sourced from multiple locations, and cross-verified for accuracy.** 🚀


## **Installation & Setup**
1. Clone the repository:
   ```sh
   git clone https://github.com/your-repo-name.git
   cd your-repo-name
2. Create a virtual environment and install the requirements:
   ```sh
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
3. Set up environment variables using the .env.sample as a reference.
4. Run the application using the file
    ```sh
    app.agents.graphs.GraphBuilder
   

<img width="546" alt="Screenshot 2024-12-31 at 11 09 42 PM" src="https://github.com/user-attachments/assets/e520e803-1c64-4890-849f-d45901353618" />


<img width="1230" alt="Screenshot 2025-01-02 at 1 12 46 PM" src="https://github.com/user-attachments/assets/058fddf1-6e07-4be6-8799-fa03380f2ce0" />
