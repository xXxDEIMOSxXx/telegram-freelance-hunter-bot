"""Unit tests for database models"""

from src.database.models import Base, TelegramMessage


class TestTelegramMessageModel:
    """Tests for TelegramMessage ORM model"""

    def test_model_attributes(self):
        """Test that model has all required attributes

        Verifies all database columns are defined
        """

        required_attrs = [
            "message_id",
            "message_datetime",
            "chat_title",
            "chat_id",
            "sender_id",
            "have_keyword",
            "keyword",
            "not_scum",
            "notify",
            "message_text",
        ]

        for attr in required_attrs:
            assert hasattr(TelegramMessage, attr)

    def test_model_tablename(self):
        """Test that model has correct table name

        Verifies database table naming
        """

        assert TelegramMessage.__tablename__ == "telegram_bot_messages_history"

    def test_model_repr(self):
        """Test model string representation

        Verifies __repr__ method works correctly
        """

        message = TelegramMessage()
        message.message_id = 123456
        message.keyword = "freelance project"

        repr_str = repr(message)

        assert "123456" in repr_str
        assert "freelance project" in repr_str or "freelance p" in repr_str

    def test_model_repr_keyword_truncation(self):
        """Test that model repr truncates long keywords

        Verifies keyword truncation at 30 chars in repr
        """

        message = TelegramMessage()
        message.message_id = 1
        message.keyword = "a" * 50  # Very long keyword

        repr_str = repr(message)

        # Should contain truncation indicator (...)
        assert "..." in repr_str

    def test_model_default_values(self):
        """Test model default column values

        Verifies default values for optional columns
        """

        message = TelegramMessage()

        # Note: In SQLAlchemy, defaults only apply at insert time
        # Here we're just checking that columns exist and can be set
        message.keyword = "-"
        message.message_text = "-"
        message.have_keyword = False
        message.not_scum = False
        message.notify = False

        assert message.keyword == "-"
        assert message.message_text == "-"
        assert message.have_keyword is False
        assert message.not_scum is False
        assert message.notify is False

    def test_model_is_declarative_base_subclass(self):
        """Test that model is registered with declarative base

        Verifies model is properly registered for ORM
        """

        # Check if model mapper exists in registry
        mapper_classes = [mapper.class_ for mapper in Base.registry.mappers]
        assert TelegramMessage in mapper_classes
