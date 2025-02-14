
# **Finanalyser: Financial Analysis Multi-Agent Research Tool**

## **Overview**
This project is a **multi-agent hierarchical financial analysis research tool** built using LangGraph. It demonstrates how **hierarchical multi-agent frameworks** can be implemented for financial data analysis, research, and prediction.

The system consists of **four major components**, each handled by specialized agents:

1. **Data Fetching & Question Answering**  
   - If a user asks a question about financial data (e.g., *"What is Apple's current stock price?"*), the system fetches data from sources like `yfinance` and stores it in a database.  
   - Once the data is available, the system answers the question using the stored information.  

2. **Financial Data Ingestion & Q/A**  
   - Allows ingestion of structured financial documents, such as **balance sheets, income statements, and cash flow statements**.  
   - Users can perform **question-answering** on the ingested data to extract insights.  

3. **Web Scraping & Search**  
   - When external financial data is needed, the system can **search the web** for relevant information using a search API.  
   - If deeper extraction is required, a **web scraper** retrieves data from a specific URL.  

4. **Data Prediction**  
   - Uses predictive algorithms to forecast financial trends based on historical data.  
   - Helps in estimating future stock movements or financial performance.  

---

## **Technology Stack**
- **Python** (Main backend development)
- **LangGraph** (Hierarchical multi-agent framework)
- **yfinance** (Stock market data retrieval)
- **FAISS** (Vector store for efficient document retrieval)
- **PostgreSQL** (Database for storing financial data)
- **Web Scraping APIs** (For real-time financial data extraction)

---

## **How It Works**
1. **User requests financial data** → The system fetches data and answers the query.
2. **User uploads financial documents** → The system ingests and allows Q/A on it.
3. **User requests external financial insights** → The system searches the web and scrapes data if needed.
4. **User wants predictions** → The system applies financial forecasting algorithms.

Each step is handled by a **dedicated agent**, and the **Supervisor Node** orchestrates the workflow, ensuring a structured and efficient analysis process.

---

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
