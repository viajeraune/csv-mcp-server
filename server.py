import os
import json
import pandas as pd
import numpy as np
from typing import Any, List
from mcp.server.fastmcp import FastMCP
from pathlib import Path
import csv

# Initialize FastMCP server
mcp = FastMCP("csv-analyzer")

# ============================================================================
# TOOLS 
# ============================================================================

@mcp.tool()
def list_csv_files(directory: str = ".") -> str:
    """
    List CSV files in a directory (similar to list_spreadsheets)
    
    Args:
        directory: Directory path to search for CSV files (default: current directory)
    
    Returns:
        JSON string with CSV file names, paths, and basic info
    """
    try:
        path = Path(directory).expanduser().resolve()
        
        if not path.exists():
            return json.dumps({
                'error': f'Directory not found: {directory}'
            }, indent=2)
        
        # Find all CSV files
        csv_files = []
        for csv_path in path.glob("**/*.csv"):
            try:
                # Get basic file info
                stat = csv_path.stat()
                
                # Quick peek at first row for column count
                with open(csv_path, 'r', encoding='utf-8') as f:
                    reader = csv.reader(f)
                    first_row = next(reader, None)
                    col_count = len(first_row) if first_row else 0
                
                # Count rows (approximate)
                with open(csv_path, 'r', encoding='utf-8') as f:
                    row_count = sum(1 for _ in f) - 1  # Subtract header
                
                csv_files.append({
                    'name': csv_path.name,
                    'path': str(csv_path),
                    'size_mb': round(stat.st_size / (1024 * 1024), 2),
                    'rows': row_count,
                    'columns': col_count,
                    'modified': stat.st_mtime
                })
            except Exception as e:
                csv_files.append({
                    'name': csv_path.name,
                    'path': str(csv_path),
                    'error': str(e)
                })
        
        return json.dumps({
            'directory': str(path),
            'csv_files': csv_files,
            'total_files': len(csv_files)
        }, indent=2)
    
    except Exception as e:
        return json.dumps({
            'error': str(e)
        }, indent=2)


@mcp.tool()
def read_csv(filepath: str, rows: int = 100) -> str:
    """
    Read data from a CSV file (similar to read_sheet)
    
    Args:
        filepath: Path to the CSV file
        rows: Maximum number of rows to return (default: 100)
    
    Returns:
        JSON string with CSV data
    """
    try:
        path = Path(filepath).expanduser().resolve()
        
        if not path.exists():
            return json.dumps({
                'error': f'File not found: {filepath}'
            }, indent=2)
        
        # Read CSV
        df = pd.read_csv(path, nrows=rows)
        
        return json.dumps({
            'filepath': str(path),
            'total_rows': len(df),
            'columns': df.columns.tolist(),
            'data': df.to_dict(orient='records')
        }, indent=2)
    
    except Exception as e:
        return json.dumps({
            'error': str(e),
            'filepath': filepath
        }, indent=2)


@mcp.tool()
def write_csv(filepath: str, data: List[List[Any]], headers: List[str] = None) -> str:
    """
    Write data to a CSV file (similar to write_sheet)
    
    Args:
        filepath: Path where to write the CSV file
        data: 2D list of values to write
        headers: Optional list of column headers
    
    Returns:
        Confirmation message
    """
    try:
        path = Path(filepath).expanduser().resolve()
        
        # Create parent directories if they don't exist
        path.parent.mkdir(parents=True, exist_ok=True)
        
        # Create DataFrame
        if headers:
            df = pd.DataFrame(data, columns=headers)
        else:
            df = pd.DataFrame(data)
        
        # Write to CSV
        df.to_csv(path, index=False)
        
        return json.dumps({
            'status': 'success',
            'filepath': str(path),
            'rows_written': len(df),
            'columns_written': len(df.columns)
        }, indent=2)
    
    except Exception as e:
        return json.dumps({
            'error': str(e),
            'filepath': filepath
        }, indent=2)


@mcp.tool()
def append_csv(filepath: str, data: List[List[Any]]) -> str:
    """
    Append data to an existing CSV file (similar to append_sheet)
    
    Args:
        filepath: Path to the CSV file
        data: 2D list of values to append
    
    Returns:
        Confirmation message
    """
    try:
        path = Path(filepath).expanduser().resolve()
        
        if not path.exists():
            return json.dumps({
                'error': f'File not found: {filepath}. Use write_csv to create a new file.'
            }, indent=2)
        
        # Read existing CSV to get headers
        existing_df = pd.read_csv(path)
        
        # Create DataFrame with same columns
        new_df = pd.DataFrame(data, columns=existing_df.columns)
        
        # Append to CSV
        new_df.to_csv(path, mode='a', header=False, index=False)
        
        return json.dumps({
            'status': 'success',
            'filepath': str(path),
            'rows_appended': len(new_df)
        }, indent=2)
    
    except Exception as e:
        return json.dumps({
            'error': str(e),
            'filepath': filepath
        }, indent=2)


@mcp.tool()
def create_csv(filepath: str, headers: List[str]) -> str:
    """
    Create a new CSV file with headers (similar to create_spreadsheet)
    
    Args:
        filepath: Path for the new CSV file
        headers: List of column headers
    
    Returns:
        JSON with file path and info
    """
    try:
        path = Path(filepath).expanduser().resolve()
        
        # Create parent directories if they don't exist
        path.parent.mkdir(parents=True, exist_ok=True)
        
        # Create empty DataFrame with headers
        df = pd.DataFrame(columns=headers)
        
        # Write to CSV
        df.to_csv(path, index=False)
        
        return json.dumps({
            'status': 'success',
            'filepath': str(path),
            'headers': headers,
            'message': f'Created new CSV file with {len(headers)} columns'
        }, indent=2)
    
    except Exception as e:
        return json.dumps({
            'error': str(e),
            'filepath': filepath
        }, indent=2)


@mcp.tool()
def get_csv_info(filepath: str) -> str:
    """
    Get detailed information about a CSV file
    
    Args:
        filepath: Path to the CSV file
    
    Returns:
        JSON with detailed CSV information
    """
    try:
        path = Path(filepath).expanduser().resolve()
        
        if not path.exists():
            return json.dumps({
                'error': f'File not found: {filepath}'
            }, indent=2)
        
        # Read CSV
        df = pd.read_csv(path)
        
        # Get file stats
        stat = path.stat()
        
        info = {
            'filepath': str(path),
            'filename': path.name,
            'size_mb': round(stat.st_size / (1024 * 1024), 2),
            'modified': stat.st_mtime,
            'shape': {
                'rows': len(df),
                'columns': len(df.columns)
            },
            'columns': df.columns.tolist(),
            'dtypes': {col: str(dtype) for col, dtype in df.dtypes.items()},
            'memory_usage_mb': round(df.memory_usage(deep=True).sum() / (1024 * 1024), 2)
        }
        
        return json.dumps(info, indent=2)
    
    except Exception as e:
        return json.dumps({
            'error': str(e),
            'filepath': filepath
        }, indent=2)


@mcp.tool()
def analyze_csv(filepath: str) -> str:
    """
    Get comprehensive statistical analysis of a CSV file
    
    Args:
        filepath: Path to the CSV file
    
    Returns:
        JSON with summary statistics and analysis
    """
    try:
        path = Path(filepath).expanduser().resolve()
        
        if not path.exists():
            return json.dumps({
                'error': f'File not found: {filepath}'
            }, indent=2)
        
        # Read CSV
        df = pd.read_csv(path)
        
        analysis = {
            'filepath': str(path),
            'shape': {
                'rows': len(df),
                'columns': len(df.columns)
            },
            'columns': {},
            'missing_values': df.isnull().sum().to_dict(),
            'duplicate_rows': int(df.duplicated().sum())
        }
        
        # Analyze each column
        for col in df.columns:
            col_info = {
                'dtype': str(df[col].dtype),
                'non_null_count': int(df[col].count()),
                'null_count': int(df[col].isnull().sum()),
                'null_percentage': round(df[col].isnull().sum() / len(df) * 100, 2)
            }
            
            # Numeric column analysis
            if pd.api.types.is_numeric_dtype(df[col]):
                col_info['statistics'] = {
                    'mean': float(df[col].mean()) if not pd.isna(df[col].mean()) else None,
                    'median': float(df[col].median()) if not pd.isna(df[col].median()) else None,
                    'std': float(df[col].std()) if not pd.isna(df[col].std()) else None,
                    'min': float(df[col].min()) if not pd.isna(df[col].min()) else None,
                    'max': float(df[col].max()) if not pd.isna(df[col].max()) else None,
                    'q25': float(df[col].quantile(0.25)) if not pd.isna(df[col].quantile(0.25)) else None,
                    'q75': float(df[col].quantile(0.75)) if not pd.isna(df[col].quantile(0.75)) else None
                }
                
                # Outlier detection
                Q1 = df[col].quantile(0.25)
                Q3 = df[col].quantile(0.75)
                IQR = Q3 - Q1
                outliers = df[col][(df[col] < Q1 - 1.5 * IQR) | (df[col] > Q3 + 1.5 * IQR)]
                col_info['outliers'] = {
                    'count': len(outliers),
                    'percentage': round(len(outliers) / len(df) * 100, 2)
                }
            
            # Categorical column analysis
            elif pd.api.types.is_object_dtype(df[col]) or pd.api.types.is_categorical_dtype(df[col]):
                value_counts = df[col].value_counts().head(10)
                col_info['unique_count'] = int(df[col].nunique())
                col_info['top_values'] = {str(k): int(v) for k, v in value_counts.items()}
            
            analysis['columns'][col] = col_info
        
        return json.dumps(analysis, indent=2)
    
    except Exception as e:
        return json.dumps({
            'error': str(e),
            'filepath': filepath
        }, indent=2)

@mcp.tool()
def categorize_by_product(filepath: str, categories_filepath: str = "test_data/product_categories.csv") -> str:
    """
    Categorize user queries from a CSV file into relevant product areas
    
    Args:
        filepath: Path to the CSV file containing user queries (must have 'query' column)
        categories_filepath: Path to the product categories CSV file (default: test_data/product_categories.csv)
    
    Returns:
        JSON with categorized queries and statistics
    """
    try:
        # Resolve file paths
        queries_path = Path(filepath).expanduser().resolve()
        if not queries_path.exists():
            return json.dumps({
                'error': f'Queries file not found: {filepath}'
            }, indent=2)

        categories_path = Path(categories_filepath).expanduser().resolve()
        if not categories_path.exists():
            return json.dumps({
                'error': f'Categories file not found: {categories_filepath}'
            }, indent=2)
        
        # Load data
        queries_df = pd.read_csv(queries_path)
        categories_df = pd.read_csv(categories_path)
        
        # Check if 'query' column exists
        if 'query' not in queries_df.columns:
            return json.dumps({
                'error': 'CSV file must contain a "query" column'
            }, indent=2)
        
        # Validate categories file columns
        if not {'product_area', 'keywords'}.issubset(set(categories_df.columns)):
            return json.dumps({
                'error': 'Categories CSV must contain columns: product_area, keywords',
                'found_columns': categories_df.columns.tolist()
            }, indent=2)
        
        # Build keyword mapping from categories CSV
        category_keywords = {}
        for _, row in categories_df.iterrows():
            product_area = str(row['product_area']).strip()
            raw_keywords = str(row.get('keywords', '') or '')
            if not product_area:
                continue
            keywords = [kw.strip().lower() for kw in raw_keywords.split(',') if kw.strip()]
            if keywords:
                category_keywords[product_area] = keywords
        
        if not category_keywords:
            return json.dumps({
                'error': 'No keywords found in categories CSV',
                'categories_filepath': str(categories_path)
            }, indent=2)
        
        def categorize_query(query_text: Any) -> str:
            """Categorize a single query based on keyword matching from CSV."""
            if pd.isna(query_text):
                return 'Uncategorized'
            
            query_lower = str(query_text).lower()
            best_category = 'Uncategorized'
            best_score = 0
            
            for category, keywords in category_keywords.items():
                score = 0
                for keyword in keywords:
                    if not keyword:
                        continue
                    if keyword in query_lower:
                        # Basic scoring: count matches; longer keywords are weighted slightly higher
                        score += 1
                        if len(keyword) >= 8:
                            score += 1
                if score > best_score:
                    best_score = score
                    best_category = category
            
            return best_category
        
        # Apply categorization to all queries
        queries_df['product_category'] = queries_df['query'].apply(categorize_query)
        
        # Build output filename (same folder, with "_categorized" appended)
        output_path = queries_path.with_name(
            f"{queries_path.stem}_categorized{queries_path.suffix}"
        )
        queries_df.to_csv(output_path, index=False)
        
        # Generate statistics
        category_counts = queries_df['product_category'].value_counts()
        stats = {
            'total_queries': len(queries_df),
            'categorized_queries': int((queries_df['product_category'] != 'Uncategorized').sum()),
            'uncategorized_queries': int((queries_df['product_category'] == 'Uncategorized').sum()),
            'category_distribution': {k: int(v) for k, v in category_counts.to_dict().items()},
            'top_categories': {k: int(v) for k, v in category_counts.head(10).to_dict().items()}
        }
        
        results = {
            'status': 'success',
            'filepath': str(queries_path),
            'output_filepath': str(output_path),
            'categories_filepath': str(categories_path),
            'statistics': stats,
            # 'categorized_data': queries_df[['query', 'product_category']].to_dict('records')
        }
        
        return json.dumps(results, indent=2)
    
    except Exception as e:
        return json.dumps({
            'error': str(e),
            'filepath': filepath,
            'categories_filepath': categories_filepath
        }, indent=2)
        
@mcp.tool()
def filter_csv(filepath: str, column: str, operator: str, value: str, 
               output_path: str = None) -> str:
    """
    Filter CSV data and optionally save to new file
    
    Args:
        filepath: Path to the CSV file
        column: Column name to filter on
        operator: Comparison operator (==, !=, >, <, >=, <=, contains)
        value: Value to compare against
        output_path: Optional path to save filtered data
    
    Returns:
        JSON with filtered data info
    """
    try:
        path = Path(filepath).expanduser().resolve()
        
        if not path.exists():
            return json.dumps({
                'error': f'File not found: {filepath}'
            }, indent=2)
        
        df = pd.read_csv(path)
        
        if column not in df.columns:
            return json.dumps({
                'error': f'Column "{column}" not found in CSV'
            }, indent=2)
        
        # Apply filter
        if operator == '==':
            filtered_df = df[df[column] == value]
        elif operator == '!=':
            filtered_df = df[df[column] != value]
        elif operator == '>':
            filtered_df = df[df[column] > float(value)]
        elif operator == '<':
            filtered_df = df[df[column] < float(value)]
        elif operator == '>=':
            filtered_df = df[df[column] >= float(value)]
        elif operator == '<=':
            filtered_df = df[df[column] <= float(value)]
        elif operator == 'contains':
            filtered_df = df[df[column].astype(str).str.contains(value, na=False)]
        else:
            return json.dumps({
                'error': f'Unknown operator: {operator}'
            }, indent=2)
        
        result = {
            'original_rows': len(df),
            'filtered_rows': len(filtered_df),
            'filter': f'{column} {operator} {value}',
            'sample_data': filtered_df.head(20).to_dict(orient='records')
        }
        
        # Save to file if output path provided
        if output_path:
            output = Path(output_path).expanduser().resolve()
            output.parent.mkdir(parents=True, exist_ok=True)
            filtered_df.to_csv(output, index=False)
            result['output_path'] = str(output)
        
        return json.dumps(result, indent=2)
    
    except Exception as e:
        return json.dumps({
            'error': str(e),
            'filepath': filepath
        }, indent=2)


@mcp.tool()
def merge_csvs(filepath1: str, filepath2: str, output_path: str, 
               on: str = None, how: str = 'inner') -> str:
    """
    Merge two CSV files
    
    Args:
        filepath1: Path to first CSV file
        filepath2: Path to second CSV file
        output_path: Path for merged output file
        on: Column name to merge on (optional)
        how: Type of merge (inner, outer, left, right)
    
    Returns:
        JSON with merge results
    """
    try:
        path1 = Path(filepath1).expanduser().resolve()
        path2 = Path(filepath2).expanduser().resolve()
        
        if not path1.exists():
            return json.dumps({'error': f'File not found: {filepath1}'}, indent=2)
        if not path2.exists():
            return json.dumps({'error': f'File not found: {filepath2}'}, indent=2)
        
        df1 = pd.read_csv(path1)
        df2 = pd.read_csv(path2)
        
        # Merge DataFrames
        if on:
            merged_df = pd.merge(df1, df2, on=on, how=how)
        else:
            merged_df = pd.merge(df1, df2, how=how)
        
        # Save merged data
        output = Path(output_path).expanduser().resolve()
        output.parent.mkdir(parents=True, exist_ok=True)
        merged_df.to_csv(output, index=False)
        
        return json.dumps({
            'status': 'success',
            'file1_rows': len(df1),
            'file2_rows': len(df2),
            'merged_rows': len(merged_df),
            'output_path': str(output),
            'merge_type': how,
            'merge_on': on
        }, indent=2)
    
    except Exception as e:
        return json.dumps({
            'error': str(e)
        }, indent=2)




# ============================================================================
# RESOURCES - Provide access to CSV data
# ============================================================================

@mcp.resource("csv://{filepath}")
def get_csv_resource(filepath: str) -> str:
    """
    Resource for accessing CSV file data (similar to sheet resource)
    
    Args:
        filepath: Path to the CSV file
    
    Returns:
        CSV data as formatted text
    """
    try:
        path = Path(filepath).expanduser().resolve()
        
        if not path.exists():
            return f"Error: File not found: {filepath}"
        
        df = pd.read_csv(path)
        
        # Format as readable text
        output = []
        output.append(f"CSV File: {path.name}")
        output.append(f"Rows: {len(df)}, Columns: {len(df.columns)}")
        output.append("-" * 80)
        
        # Add headers
        output.append(" | ".join(df.columns.tolist()))
        output.append("-" * 80)
        
        # Add data rows (first 50)
        for _, row in df.head(50).iterrows():
            output.append(" | ".join(str(val) for val in row))
        
        if len(df) > 50:
            output.append(f"... and {len(df) - 50} more rows")
        
        return "\n".join(output)
    
    except Exception as e:
        return f"Error reading CSV: {str(e)}"


# ============================================================================
# PROMPTS - Analysis workflows
# ============================================================================

@mcp.prompt()
def analyze_csv_data():
    """Analyze data from a CSV file with comprehensive insights"""
    return """I need help analyzing data from a CSV file. Please follow this workflow:

1. **Data Retrieval & Overview**
   - Ask me for the CSV file path (or help me list CSV files if needed)
   - Read the CSV data using the read_csv tool
   - Provide a high-level summary:
     * Total number of rows and columns
     * Column headers/names
     * File size and basic info
     * Brief description of what type of data this appears to be

2. **Data Structure Analysis**
   - Identify data types in each column (text, numeric, dates, categorical, etc.)
   - Note which columns contain responses vs. metadatata
   - Check for missing, empty, or inconsistent values
   - Identify any obvious patterns in data organization
   - Note any duplicate rows

3. **Quantitative Analysis** (where applicable)
   - Use analyze_csv tool for comprehensive statistics 
   - For numeric columns: averages, ranges (min/max), standard deviation
   - For categorical data: frequency distributions, most common values
   - For rating scales: score distributions and averages
   - Identify any outliers or unusual values

4. **Qualitative Insights** (where applicable)
   - Summarize themes in text columns
   - Identify common keywords or categories
   - Note any particularly interesting or concerning patterns
   - Highlight consensus vs. divergent values

5. **Key Findings & Recommendations**
   - Summarize 3-5 most important insights from the data
   - Flag any data quality issues or anomalies
   - Suggest improvements (data cleaning, additional fields, validation)
   - Recommend next steps for analysis or action
   - Propose potential visualizations that would make the data clearer

Please present findings in a clear, scannable format with specific examples and numbers from the actual data."""


@mcp.prompt()
def create_report_from_csv():
    """Create a professional report document from CSV analysis"""
    return """Help me create a professional data analysis report from CSV data. Please create this as a well-formatted markdown document:

1. **Report Header**
   - Report title 
   - Report data period/date range (if applicable from data)
   - Date generated

2. **Executive Summary**
   - Brief overview of key findings (2-3 paragraphs)
   - Highlight the most critical insights
   - Bottom-line recommendation or conclusion

3. **Key Metrics Dashboard**
   - Create a clean table with columns: Metric | Value | Change | Status
   - Include 3-6 most relevant metrics with placeholder values
   - Add brief context notes below the table

4. **Detailed Analysis**
   - Break down findings into logical sections
   - Use clear headers for each topic area
   - Include supporting data and statistics
   - Present information in scannable format with tables

5. **Findings & Recommendations**
   - **Key Findings**: List 3-5 most important discoveries
   - **Data Quality Issues**: Any problems found
   - **Recommendations**: Specific, actionable suggestions
   - **Action Items**: Table with columns for Item, Owner, Due Date, Priority

6. **Appendix**
   - Methodology, analysis approach, data sources, etc.
   - Assumptions made
   - Areas for further investigation
   - Additional context or supporting information

Please format the report with:
- Clear hierarchy using markdown headers
- Professional tables for data presentation
- Bold text for emphasis on key points
- Appropriate spacing for readability
- Specific data points and examples from the CSV
- Placeholder content that can be easily customized"""


@mcp.prompt()
def compare_csvs():
    """Compare two CSV files and identify differences"""
    return """Help me compare two CSV files. Please follow this workflow:

1. **Get File Paths**
   - Ask me for the paths to both CSV files
   - Or help me list available CSV files if needed

2. **Basic Comparison**
   - Compare file sizes and row counts
   - Compare column names and types
   - Identify any structural differences

3. **Data Comparison**
   - If files have same structure, identify:
     * New rows in file 2
     * Missing rows from file 1
     * Changed values
   - If different structures:
     * Identify common columns
     * Compare data in common columns
     * Note unique columns in each file

4. **Statistical Comparison**
   - For numeric columns that exist in both:
     * Compare means, medians, ranges
     * Note any significant differences
   - For categorical columns:
     * Compare value distributions
     * Identify new or missing categories

5. **Summary Report**
   - Create a clear summary of all differences
   - Highlight the most significant changes
   - Recommend whether files should be merged or kept separate
   - Suggest next steps

Present the comparison in a clear, structured format with specific examples."""


@mcp.prompt()
def clean_csv_data():
    """Guide through cleaning and preparing CSV data"""
    return """Help me clean and prepare CSV data for analysis. Please follow this workflow:

1. **Initial Assessment**
   - Analyze the CSV file using analyze_csv tool
   - Identify all data quality issues:
     * Missing values
     * Duplicate rows
     * Inconsistent formatting
     * Outliers
     * Invalid data types

2. **Propose Cleaning Steps**
   - For each issue found, propose specific fixes:
     * How to handle missing values (drop, fill, interpolate)
     * Which duplicates to remove
     * How to standardize formats
     * How to handle outliers
   - Explain the reasoning for each recommendation

3. **Create Cleaned Version**
   - Once approved, create a cleaned CSV file
   - Document all transformations made
   - Save to a new file (never overwrite original)
   - Name it clearly (e.g., original_cleaned.csv)

4. **Validation**
   - Analyze the cleaned CSV
   - Compare before/after statistics
   - Confirm all issues were addressed
   - Document any remaining limitations

5. **Documentation**
   - Create a summary of:
     * Original data issues
     * Cleaning steps performed
     * Records affected
     * Final data quality assessment
   - Provide both file paths (original and cleaned)

Present each step clearly and wait for approval before making changes."""

if __name__ == "__main__":
    # Run the server with stdio transport for local usage
    mcp.run(transport='stdio')