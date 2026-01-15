"""
Structured logging for safety-critical medical imaging pipeline.

All logs are designed to be auditable and traceable.
"""
import logging
import sys
import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional


class StructuredFormatter(logging.Formatter):
    """Formatter that outputs structured JSON logs."""
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON."""
        log_data = {
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno
        }
        
        # Add exception info if present
        if record.exc_info:
            log_data['exception'] = self.formatException(record.exc_info)
        
        # Add extra fields if present
        if hasattr(record, 'extra_fields'):
            log_data.update(record.extra_fields)
        
        return json.dumps(log_data)


class PipelineLogger:
    """Logger wrapper with pipeline-specific convenience methods."""
    
    def __init__(self, name: str, level: str = 'INFO'):
        """
        Initialize pipeline logger.
        
        Args:
            name: Logger name
            level: Logging level (DEBUG, INFO, WARNING, ERROR)
        """
        self.logger = logging.getLogger(name)
        self.logger.setLevel(getattr(logging, level))
        
        # Remove existing handlers
        self.logger.handlers.clear()
        
        # Console handler with structured format
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(StructuredFormatter())
        self.logger.addHandler(console_handler)
    
    def log_stage_start(self, stage_name: str, **kwargs: Any) -> None:
        """Log start of pipeline stage."""
        self.logger.info(
            f"Starting stage: {stage_name}",
            extra={'extra_fields': {'stage': stage_name, 'event': 'stage_start', **kwargs}}
        )
    
    def log_stage_complete(self, stage_name: str, **kwargs: Any) -> None:
        """Log completion of pipeline stage."""
        self.logger.info(
            f"Completed stage: {stage_name}",
            extra={'extra_fields': {'stage': stage_name, 'event': 'stage_complete', **kwargs}}
        )
    
    def log_validation_result(self, is_valid: bool, details: Dict[str, Any]) -> None:
        """Log validation result."""
        level = logging.INFO if is_valid else logging.ERROR
        self.logger.log(
            level,
            f"Validation {'passed' if is_valid else 'failed'}",
            extra={'extra_fields': {'event': 'validation', 'is_valid': is_valid, **details}}
        )
    
    def log_metrics(self, metrics: Dict[str, Any]) -> None:
        """Log quantitative metrics."""
        self.logger.info(
            "Computed metrics",
            extra={'extra_fields': {'event': 'metrics', **metrics}}
        )
    
    def log_configuration(self, config: Dict[str, Any]) -> None:
        """Log pipeline configuration for traceability."""
        self.logger.info(
            "Pipeline configuration",
            extra={'extra_fields': {'event': 'configuration', **config}}
        )
    
    def log_file_io(self, operation: str, filepath: Path, checksum: Optional[str] = None) -> None:
        """Log file I/O operation."""
        extra = {
            'event': 'file_io',
            'operation': operation,
            'filepath': str(filepath)
        }
        if checksum:
            extra['checksum'] = checksum
        
        self.logger.info(
            f"File {operation}: {filepath}",
            extra={'extra_fields': extra}
        )
    
    def add_file_handler(self, log_file: Path) -> None:
        """Add file handler for persistent logging."""
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(StructuredFormatter())
        self.logger.addHandler(file_handler)


def create_pipeline_logger(name: str, level: str, output_dir: Optional[Path] = None) -> PipelineLogger:
    """
    Create configured pipeline logger.
    
    Args:
        name: Logger name
        level: Logging level
        output_dir: Optional directory for log file
        
    Returns:
        Configured PipelineLogger instance
    """
    logger = PipelineLogger(name, level)
    
    if output_dir is not None:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        log_file = output_dir / f'pipeline_{timestamp}.log'
        logger.add_file_handler(log_file)
    
    return logger
