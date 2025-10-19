# CSV Analyzer MCP Server (Local)

A **local** Model Context Protocol (MCP) server for analyzing CSV files directly from your filesystem. Specifically designed for chatbot conversation logs analysis, such as analyzing customer support logs, chatbot interactions, and any conversational data stored in CSV format.

## Features

- 📁 **List CSV files** in directories
- 📖 **Read and analyze** conversation logs
- ✍️ **Create and write** analysis reports
- ➕ **Append data** for custom log addition
- 🔍 **Filter and query** specific logs
- 🔗 **Merge multiple** log files from different time periods
- 📊 **Statistical analysis** of conversation metrics
- 💬 **Conversational insights** by custom topics (e.g. product area), user intent, sentiment
- 🤖 **AI-guided prompts** for analysis workflows

## Why Local?

This server uses **local file access** (not remote HTTP), which means:
- ✅ Direct filesystem access - just provide file paths
- ✅ Works with large CSV files efficiently
- ✅ No file upload/download needed
- ✅ Better security - files stay on your machine
- ✅ Simpler setup - no ports or networking
- ✅ Perfect for personal CSV analysis

## Installation

### Prerequisites

- Python 3.8 or higher
- Claude Desktop app

### Step 1: Clone or Download

```bash
# Clone repository
git clone https://github.com/YOUR_USERNAME/csv-mcp-server.git
cd csv-mcp-server

# Or download and extract the ZIP file
```

### Step 2: Create Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate it
# On macOS/Linux:
source venv/bin/activate

# On Windows:
venv\Scripts\activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Test the Server with MCP Inspector

```bash
npx @modelcontextprotocol/inspector python gsheets_server.py
```

## Configuration

### Add to Claude Desktop

1. **Find your config file location:**
   - **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
   - **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

2. **Edit the config file** (create if it doesn't exist):

```json
{
  "mcpServers": {
    "csv-analyzer": {
      "command": "python",
      "args": ["/absolute/path/to/csv-mcp-server/server.py"]
    }
  }
}
```

**Important**: Replace `/absolute/path/to/csv-mcp-server/server.py` with your actual path!

**Example paths:**
- macOS: `/Users/yourname/projects/csv-mcp-server/server.py`
- Windows: `C:\\Users\\yourname\\projects\\csv-mcp-server\\server.py`

3. **Restart Claude Desktop**

4. **Verify it's working:**
   - Look for the 🔨 (hammer) icon in Claude Desktop
   - You should see "csv-analyzer" listed with available tools

## Usage Examples

Once configured, you can interact with CSV files naturally in Claude or Cursor:

### Example 1: List CSV Files

```
You: Show me all CSV files in my Downloads folder

Claude: [Uses list_csv_files tool]
I found 5 CSV files in your Downloads folder:
- chatbot_logs.csv (1,234 rows, 8 columns, 2.3 MB)
- customer_data.csv (5,678 rows, 12 columns, 4.1 MB)
...
```

### Example 2: Analyze a CSV

```
You: Analyze ~/Documents/chatbot_logs.csv

Claude: [Uses analyze_csv tool]
I've analyzed your chatbot_logs data. Here are the key findings:

📊 Dataset Overview:
- 1,234 rows × 8 columns
- Date range: July 2025 - September 2025
- File size: 2.3 MB

🔍 Key Insights:
1. Overall Satisfaction Rate: 94% (thumbs up)
2. Dissatisfaction Rate: 6% (thumbs down)
3. Most Common Positive Feedback: Performance optimization guidance (6 instances)
4. Most Common Negative Feedback: Need for more examples/code implementations
...
```

### Example 3: Filter and Save

```
You: Filter chatbot_logs.csv where feedback = negative and save to logs_negative_feedback.csv

Claude: [Uses filter_csv tool]
Filtered data:
- Original rows: 1,234
- Filtered rows: 187 (15.2%)
- Saved to: ~/Documents/logs_negative_feedback.csv
```

### Example 4: Merge Files

```
You: Merge customer_data.csv and chatbot_logs.csv on customer_id

Claude: [Uses merge_csvs tool]
Successfully merged files:
- customer_data.csv: 500 rows
- chatbot_logs.csv: 1,234 rows  
- Merged result: 1,234 rows
- Saved to: merged_output.csv
```

## Available Tools

### File Operations

| Tool | Description |
|------|-------------|
| `list_csv_files` | List all CSV files in a directory |
| `read_csv` | Read data from a CSV file |
| `write_csv` | Create and write a new CSV file |
| `append_csv` | Append rows to existing CSV |
| `create_csv` | Create new CSV with headers |
| `get_csv_info` | Get detailed file information |

### Analysis Tools

| Tool | Description |
|------|-------------|
| `analyze_csv` | Comprehensive statistical analysis |
| `categorize_by_product` | Keyword based categorization (e.g. Product area) |
| `filter_csv` | Filter data with conditions |
| `merge_csvs` | Merge two CSV files |

### Analysis Prompts

| Prompt | Description |
|--------|-------------|
| `analyze_csv_data` | Complete workflow for CSV analysis |
| `create_report_from_csv` | Generate professional data report |
| `compare_csvs` | Compare two CSV files |
| `clean_csv_data` | Guide through data cleaning process |

## Advanced Usage

### Custom Analysis Workflows

You can create custom analysis workflows by chaining multiple tools:

```
You: I want to analyze all CSV files in my Downloads folder, 
find the ones with sales data, filter for amounts over $1000, 
and create a summary report.

Claude: [Will use multiple tools in sequence:
1. list_csv_files to find all CSVs
2. read_csv to peek at each file
3. filter_csv on relevant files
4. analyze_csv for statistics
5. Create formatted report]
```

### Working with Large Files

For large CSV files (>100MB), the server:
- Reads data efficiently with pandas
- Can limit rows returned
- Analyzes without loading all data
- Provides streaming statistics

**Tips:**
- Use `rows` parameter to limit data read
- Filter large files before analysis
- Save filtered results to new files

### Data Cleaning Workflow

Use the `clean_csv_data` prompt for guided cleaning:

```
You: Help me clean my messy sales data at ~/messy_sales.csv

Claude: [Uses clean_csv_data prompt]
I'll analyze the data and guide you through cleaning it.

Step 1: Initial Assessment...
Found these issues:
- 23 duplicate rows (1.8%)
- Missing values in "amount" column (5%)
- Inconsistent date formats

Step 2: Recommended Fixes...
[Provides detailed recommendations]

[Once approved, creates cleaned version]
```

## Security & Privacy

### Data Privacy

- ✅ All data stays on your local machine
- ✅ No data sent to external servers
- ✅ Files accessed only via Claude Desktop
- ✅ No internet connection required

### File Permissions

The server can:
- ✅ Read CSV files you have access to
- ✅ Write new files in writable directories
- ❌ Cannot access system files
- ❌ Cannot modify without explicit command

### Best Practices

1. **Keep sensitive data local** - perfect use case for this tool
2. **Use separate folder** for analysis outputs
3. **Review changes** before overwriting files
4. **Backup important data** before cleaning operations

## Development

### Project Structure

```
csv-mcp-server/
├── server.py              # Main server implementation
├── requirements.txt       # Python dependencies
├── README.md             # This file
├── .gitignore            # Git ignore rules
├── venv/                 # Virtual environment (not in git)
├── analysis/             # Sample analysis outputs
└── test_data/            # Sample files 
```