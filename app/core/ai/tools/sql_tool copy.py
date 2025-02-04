from datetime import datetime
import re
from sqlalchemy import text, DateTime
from sqlalchemy.exc import SQLAlchemyError
from app.db.database import get_db, Base

def format_query_result(result) -> str:
    if result is None:
        return "No results"
    
    if not result:
        return "Empty result set"
    
    formatted_rows = []
    for i, row in enumerate(result, 1):
        if isinstance(row, dict):
            row_str = ", ".join([f"{k}: {v}" for k, v in row.items()])
        else:
            row_str = str(row)
        formatted_rows.append(f"Row {i}: {row_str}")
    
    return "\n".join(formatted_rows)

async def query(query_string: str):
    async for db in get_db():
        result = await db.execute(text(query_string))
        rows = result.mappings().all()
        print(f'[DH] format_query_result(rows): {format_query_result(rows)}')
        return format_query_result(rows)

async def insert(insert_statement: str, values: list[dict]):
    try:
        # Extract table name from insert statement
        table_match = re.search(r"INSERT\s+INTO\s+(\w+)", insert_statement, re.IGNORECASE)
        if not table_match:
            return {"success": False, "message": "Could not determine table from INSERT statement"}
            
        table_name = table_match.group(1)
        table = Base.metadata.tables.get(table_name)
        if not table:
            return {"success": False, "message": f"Unknown table: {table_name}"}

        # Identify datetime columns
        datetime_columns = [
            col.name for col in table.columns 
            if isinstance(col.type, DateTime)
        ]

        # Process values to convert datetime strings
        processed_values = []
        for value_set in values:
            processed = value_set.copy()
            for col in datetime_columns:
                if col in processed and isinstance(processed[col], str):
                    try:
                        # Handle ISO format with timezone offset
                        if 'T' in processed[col]:
                            processed[col] = datetime.fromisoformat(processed[col])
                        else:
                            processed[col] = datetime.strptime(processed[col], "%Y-%m-%d")
                    except ValueError as e:
                        return {
                            "success": False,
                            "message": f"Invalid datetime format for {col}: {str(e)}"
                        }
            processed_values.append(processed)

        async for db in get_db():
            try:
                await db.execute(
                    text(insert_statement),
                    processed_values
                )
                await db.commit()
                return {"success": True, "message": "Data inserted successfully"}
            except SQLAlchemyError as e:
                await db.rollback()
                return {"success": False, "message": f"Database error: {str(e)}"}
    except Exception as e:
        return {"success": False, "message": f"Unexpected error: {str(e)}"}

def get_schema_info():
    schema_info = {}
    for table_name, table in Base.metadata.tables.items():
        schema_info[table_name] = {
            "columns": [
                {"name": col.name, "type": str(col.type), "nullable": col.nullable}
                for col in table.columns
            ]
        }
    return schema_info
