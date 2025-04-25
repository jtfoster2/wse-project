import os
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, ARRAY

# from azure.identity import DefaultAzureCredential
# from azure.keyvault.secrets import SecretClient

# # Access securely stored secrets for database connection string
# credential = DefaultAzureCredential()
# vault_url = "https://contacts-key-vault.vault.azure.net/" # TODO: update this to use the actual vault name
# client = SecretClient(vault_url=vault_url, credential=credential)

# secret = "db-connection-string"
# db_connection_string = client.get_secret(secret).value

# Set up actual database
db = SQLAlchemy()

# Use environment variable for DB connection string if provided
# db connection string format should be <username>:<password>@<localhost>/<database_name>
db_connection_string = os.getenv("DB_CONNECTION_STRING", "postgres:admin@localhost:5432/postgres") # TODO: update this to use the actual database nane


class Users(db.Model):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    username = Column(String(50), nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    password = Column(String(255), nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
        }

class Extension(db.Model):
    __tablename__ = 'extension'
    id = Column(Integer, primary_key=True)
    title = Column(String(100), nullable=False)
    meta_license = Column(String(100), nullable=False)
    project_license = Column(String(100), nullable=False)
    creator = Column(Integer, ForeignKey('users.id'))
    extends = Column(String(100), nullable=False)
    summary = Column(String(255), nullable=False)
    description = Column(String(255), nullable=False)
    tags = Column(ARRAY(String), nullable=False)
    screenshots = Column(ARRAY(String), nullable=False)
    releases = Column(ARRAY(String), nullable=False)
    is_flagged = Column(Boolean, default=False)

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'meta_license': self.meta_license,
            'project_license': self.project_license,
            'creator': self.creator,
            'extends': self.extends,
            'summary': self.summary,
            'description': self.description,
            'tags': self.tags,
            'screenshots': self.screenshots,
            'releases': self.releases,
            'is_flagged': self.is_flagged
        }

class Version(db.Model):
    __tablename__ = 'version'
    id = Column(Integer, primary_key=True)
    extension_id = Column(Integer, ForeignKey('extension.id'), nullable=False)
    version = Column(String(50), nullable=False)
    plugin_url = Column(String(255), nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'extension_id': self.extension_id,
            'version': self.version,
            'plugin_url': self.plugin_url,
        }

def setup_db(app):
    app.config['SQLALCHEMY_DATABASE_URI'] = f"postgresql+psycopg2://{db_connection_string}"
    db.init_app(app)
    with app.app_context():
        db.create_all()
        add_starter_data()

def add_starter_data():
    if not db.session.query(Version).first() \
    and not db.session.query(Extension).first() \
    and not db.session.query(Users).first():
        create_starter_users()
        create_starter_extensions()
        create_starter_versions()

def create_starter_users():
    # passwords hashed using pbkdf2:sha256
    # password: "password1"
    hashed_password_1 = "pbkdf2:sha256:1000000$qht9IKspug2uA4v1$3cd5ce6b8681fe3fa8d78cf7a1d63817f6225fd2e6db662362bd4b99c0010cd5"
    # password: "password2"
    hashed_password_2 = "pbkdf2:sha256:1000000$qht9IKspug2uA4v1$3cd5ce6b8681fe3fa8d78cf7a1d63817f6225fd2e6db662362bd4b99c0010cd5"
    # password: "password3"
    hashed_password_3 = "pbkdf2:sha256:1000000$qht9IKspug2uA4v1$3cd5ce6b8681fe3fa8d78cf7a1d63817f6225fd2e6db662362bd4b99c0010cd5"

    users = [
        Users(username="user1", email="user1@example.com", password=hashed_password_1),
        Users(username="user2", email="user2@example.com", password=hashed_password_2),
        Users(username="user3", email="user3@example.com", password=hashed_password_3),
    ]
    db.session.add_all(users)
    db.session.commit()


def create_starter_extensions():
    user1 = Users.query.filter_by(username="user1").first()
    user2 = Users.query.filter_by(username="user2").first()

    ext1 = Extension(
        title="Ext A",
        meta_license="MIT",
        project_license="MIT",
        creator=user1.id,
        extends="Base1",
        summary="Summary A",
        description="Description A",
        tags=["utility", "plugin"],
        screenshots=["url1", "url2"],
        releases=["1.0.0", "1.1.0"],
    )

    ext2 = Extension(
        title="Ext B",
        meta_license="Apache",
        project_license="Apache",
        creator=user2.id,
        extends="Base2",
        summary="Summary B",
        description="Description B",
        tags=["analytics"],
        screenshots=["url3"],
        releases=["2.0.0"],
    )

    db.session.add_all([ext1, ext2])
    db.session.commit()

def create_starter_versions():
    ext1 = Extension.query.filter_by(title="Ext A").first()
    ext2 = Extension.query.filter_by(title="Ext B").first()

    versions = [
        Version(extension_id=ext1.id, version="1.0.0", plugin_url="http://example.com/extA/v1.0.0"),
        Version(extension_id=ext1.id, version="1.1.0", plugin_url="http://example.com/extA/v1.1.1.0"),
        Version(extension_id=ext2.id, version="2.0.0", plugin_url="http://example.com/extB/v2.0.0"),
    ]

    db.session.add_all(versions)
    db.session.commit()
