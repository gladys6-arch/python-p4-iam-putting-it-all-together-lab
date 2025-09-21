import pytest
from sqlalchemy.exc import IntegrityError
from app import app
from models import db, Recipe, User

class TestRecipe:
    """Tests for the Recipe model."""

    def setup_method(self):
        """Clean up the database before each test."""
        with app.app_context():
            Recipe.query.delete()
            User.query.delete()
            db.session.commit()

    def create_user(self):
        """Helper method to create a test user."""
        user = User(username="TestUser")
        user.password_hash = "secret123"
        db.session.add(user)
        db.session.commit()
        return user

    def test_has_attributes(self):
        """Recipe has title, instructions, and minutes_to_complete."""
        with app.app_context():
            user = self.create_user()

            recipe = Recipe(
                title="Delicious Shed Ham",
                instructions=(
                    "Or kind rest bred with am shed then. In raptures building an bringing be. "
                    "Elderly is detract tedious assured private so to visited. Do travelling "
                    "companions contrasted it. Mistress strongly remember up to. Ham him compass "
                    "you proceed calling detract. Better of always missed we person mr. September "
                    "smallness northward situation few her certainty something."
                ),
                minutes_to_complete=60,
                user_id=user.id
            )

            db.session.add(recipe)
            db.session.commit()

            new_recipe = Recipe.query.filter_by(title="Delicious Shed Ham").first()

            assert new_recipe.title == "Delicious Shed Ham"
            assert new_recipe.minutes_to_complete == 60
            assert "Elderly is detract tedious assured" in new_recipe.instructions

    def test_requires_title(self):
        """Requires each record to have a title."""
        with app.app_context():
            user = self.create_user()
            recipe = Recipe(
                instructions="This is a long instruction that exceeds fifty characters.",
                minutes_to_complete=30,
                user_id=user.id
            )

            with pytest.raises((IntegrityError, ValueError)) as exc_info:
                db.session.add(recipe)
                db.session.commit()

            # Optionally check the message
            assert any(msg in str(exc_info.value) for msg in [
                "NOT NULL constraint failed: recipes.title",
                "Title must be present."
            ])

    def test_requires_50_plus_char_instructions(self):
     """Instructions must be at least 50 characters."""
    with app.app_context():
        # Ensure there is a user
        user = User(username="TestUser")
        user.password_hash = "secret123"
        db.session.add(user)
        db.session.commit()

        # Catch the ValueError when setting instructions (during model creation)
        with pytest.raises(ValueError) as exc_info:
            recipe = Recipe(
                title="Generic Ham",
                instructions="Too short",  # < 50 chars
                minutes_to_complete=30,
                user_id=user.id
            )

        assert "Instructions must be at least 50 characters long." in str(exc_info.value)
