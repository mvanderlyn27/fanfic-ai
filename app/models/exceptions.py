"""Exception classes for the story service."""

class StoryServiceError(Exception):
    """Base exception class for StoryService errors"""
    pass

class TemplateError(StoryServiceError):
    """Raised when there are issues with template loading or formatting"""
    pass

class ModelError(StoryServiceError):
    """Raised when there are issues with the AI model responses"""
    pass

class ContentGenerationError(StoryServiceError):
    """Raised when there are issues generating story content"""
    pass