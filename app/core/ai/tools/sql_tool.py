import json
import logging
import re
from datetime import datetime

from sqlalchemy import JSON, DateTime, text
from sqlalchemy.exc import SQLAlchemyError

from app.db.database import Base, get_db

logger = logging.getLogger(__name__)

def _extract_table_name(sql_statement: str, operation: str):

    patterns = {
        "INSERT": r"INSERT\s+INTO\s+(\w+)",
        "UPDATE": r"UPDATE\s+(\w+)",
        "DELETE": r"DELETE\s+FROM\s+(\w+)"
    }
    match = re.search(patterns[operation], sql_statement, re.IGNORECASE)
    if not match:
        return {"success": False, "message": f"Could not determine table from {operation} statement"}
    
    table_name = match.group(1)
    table = Base.metadata.tables.get(table_name)
    # if not table:
    #     return {"success": False, "message": f"Table {table_name} not found in schema"}
    return table

def _process_data_values(table, values: list[dict]):
    datetime_columns = [col.name for col in table.columns if isinstance(col.type, DateTime)]
    processed_values = []
    
    for value_set in values:
        processed = value_set.copy()
        for col in datetime_columns:
            if col in processed and isinstance(processed[col], str):
                try:
                    processed[col] = datetime.fromisoformat(processed[col]) if 'T' in processed[col] \
                        else datetime.strptime(processed[col], "%Y-%m-%d")
                except ValueError as e:
                    return {"success": False, "message": f"Invalid datetime format for {col}: {str(e)}"}
        
        for col in table.columns:
            if isinstance(col.type, JSON) and col.name in processed:
                if isinstance(processed[col.name], (dict, list)):
                    processed[col.name] = json.dumps(processed[col.name])
        
        processed_values.append(processed)
    
    return processed_values

async def _execute_sql_statement(db, sql_statement, parameters):
    try:
        await db.execute(text(sql_statement), parameters)
        await db.commit()
        return {"success": True, "message": "Operation completed successfully"}
    except SQLAlchemyError as e:
        logger.error(f"[DH] Error executing SQL statement: {str(e)}")
        await db.rollback()
        return {"success": False, "message": f"Database error: {str(e)}"}

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
    async with get_db() as db:
        result = await db.execute(text(query_string))
        rows = result.mappings().all()
        return format_query_result(rows)

async def insert(insert_statement: str, values: list[dict]):
    logger.info(f"[DH] Inserting into database with statement: {insert_statement}")
    logger.info(f"[DH] Values: {values}")
    try:
        table = _extract_table_name(insert_statement, "INSERT")
        if isinstance(table, dict):
            return table
        
        processed_values = _process_data_values(table, values)
        if isinstance(processed_values, dict):
            return processed_values
        
        async with get_db() as db:
            return await _execute_sql_statement(db, insert_statement, processed_values)
    except Exception as e:
        return {"success": False, "message": f"Unexpected error: {str(e)}"}

async def update(update_statement: str, values: dict):
    try:
        logger.info(f"[DH] Updating database with statement: {update_statement}")
        logger.info(f"[DH] Values: {values}")
        table = _extract_table_name(update_statement, "UPDATE")
        if isinstance(table, dict):

            return table
        
        processed_values = _process_data_values(table, [values])
        if isinstance(processed_values, dict):
            return processed_values
        
        async with get_db() as db:
            return await _execute_sql_statement(db, update_statement, processed_values[0])
    except Exception as e:
        logger.error(f"[DH] Error updating database: {str(e)}")
        return {"success": False, "message": f"Unexpected error: {str(e)}"}

async def delete(delete_statement: str, values: dict):
    try:
        logger.info(f"[DH] Deleting from database with statement: {delete_statement}")
        logger.info(f"[DH] Values: {values}")
        table = _extract_table_name(delete_statement, "DELETE")
        if isinstance(table, dict):
            return table
        
        processed_values = _process_data_values(table, [values])
        if isinstance(processed_values, dict):
            return processed_values
        
        async with get_db() as db:
            return await _execute_sql_statement(db, delete_statement, processed_values[0])
    except Exception as e:
        logger.error(f"[DH] Error deleting from database: {str(e)}")

        return {"success": False, "message": f"Unexpected error: {str(e)}"}

def get_schema_info():
    schema_info = {}
    for table_name, table in Base.metadata.tables.items():
        schema_info[table_name] = {
            "columns": [
                {
                    "name": col.name,
                    "type": str(col.type),
                    "nullable": col.nullable
                }
                for col in table.columns
            ],
            "constraints": [
                {
                    "name": constraint.name or "unnamed_constraint",
                    "type": type(constraint).__name__,
                    "definition": str(constraint.sqltext) if hasattr(constraint, 'sqltext') else str(constraint)
                }
                for constraint in table.constraints
                if (constraint.name is None) or 
                   (not constraint.name.startswith('pk_') and not constraint.name.startswith('fk_'))
            ]
        }
    return schema_info
