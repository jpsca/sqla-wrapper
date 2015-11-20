# coding=utf-8
from sqlalchemy_wrapper import SQLAlchemy
from sqlalchemy_wrapper.helpers import _get_table_name
from sqlalchemy.ext.declarative import AbstractConcreteBase, declared_attr


def test_get_table_name():
    assert _get_table_name('Document') == 'documents'
    assert _get_table_name('ToDo') == 'to_dos'
    assert _get_table_name('UserTestCase') == 'user_test_cases'
    assert _get_table_name('URL') == 'urls'
    assert _get_table_name('HTTPRequest') == 'http_requests'


def test_jti_custom_tablename():
    """Test Joined Table Inheritance with a custom table name.
    """
    db = SQLAlchemy('sqlite://')

    class Person(db.Model):
        __tablename__ = 'jti_custom_people'
        id = db.Column(db.Integer, primary_key=True)
        discriminator = db.Column('type', db.String(50))
        __mapper_args__ = {'polymorphic_on': discriminator}

    class Engineer(Person):
        __tablename__ = 'jti_custom_engineers'
        __mapper_args__ = {'polymorphic_identity': 'engineer'}
        id = db.Column(db.Integer, db.ForeignKey(Person.id), primary_key=True)
        primary_language = db.Column(db.String(50))

    class Teacher(Person):
        __tablename__ = 'jti_custom_teachers'
        __mapper_args__ = {'polymorphic_identity': 'teacher'}
        id = db.Column(db.Integer, db.ForeignKey(Person.id), primary_key=True)
        primary_language = db.Column(db.String(50))

    assert Person.__tablename__ == 'jti_custom_people'
    assert Engineer.__tablename__ == 'jti_custom_engineers'
    assert Teacher.__tablename__ == 'jti_custom_teachers'
    db.session.expunge_all()


def test_jti_auto_tablename():
    """Test Joined Table Inheritance with an autonatically
    asigned table name.
    """
    db = SQLAlchemy('sqlite://')

    class JaPerson(db.Model):
        id = db.Column(db.Integer, primary_key=True)
        discriminator = db.Column('type', db.String(50))
        __mapper_args__ = {'polymorphic_on': discriminator}

    class JaEngineer(JaPerson):
        __mapper_args__ = {'polymorphic_identity': 'engineer'}
        id = db.Column(db.Integer, db.ForeignKey(JaPerson.id), primary_key=True)
        primary_language = db.Column(db.String(50))

    class JaTeacher(JaPerson):
        __tablename__ = 'jti_auto_teachers'
        __mapper_args__ = {'polymorphic_identity': 'teacher'}
        id = db.Column(db.Integer, db.ForeignKey(JaPerson.id), primary_key=True)
        primary_language = db.Column(db.String(50))

    assert JaPerson.__tablename__ == 'ja_people'
    assert JaEngineer.__tablename__ == 'ja_engineers'
    assert JaTeacher.__tablename__ == 'jti_auto_teachers'
    db.session.expunge_all()


def test_sti_custom_tablename():
    """Test Single Table Inheritance with a custom table name.
    """
    db = SQLAlchemy('sqlite://')

    class Employee(db.Model):
        __tablename__ = 'sti_custom_employee'

        id = db.Column(db.Integer, primary_key=True)
        name = db.Column(db.String(50))
        manager_data = db.Column(db.String(50))
        engineer_info = db.Column(db.String(50))
        type = db.Column(db.String(20))

        __mapper_args__ = {
            'polymorphic_on': type,
            'polymorphic_identity': 'employee'
        }

    class Manager(Employee):
        __mapper_args__ = {
            'polymorphic_identity': 'manager'
        }

    class Engineer(Employee):
        __mapper_args__ = {
            'polymorphic_identity': 'engineer'
        }

    assert Employee.__tablename__ == 'sti_custom_employee'
    assert Manager.__tablename__ == 'sti_custom_employee'
    assert Engineer.__tablename__ == 'sti_custom_employee'
    db.session.expunge_all()


def test_sti_auto_tablename():
    """Test Single Table Inheritance with an autonatically
    asigned table name.
    """
    db = SQLAlchemy('sqlite://')

    class SaEmployee(db.Model):
        id = db.Column(db.Integer, primary_key=True)
        name = db.Column(db.String(50))
        manager_data = db.Column(db.String(50))
        engineer_info = db.Column(db.String(50))
        type = db.Column(db.String(20))

        __mapper_args__ = {
            'polymorphic_on': type,
            'polymorphic_identity': 'employee'
        }

    class SaManager(SaEmployee):
        __mapper_args__ = {
            'polymorphic_identity': 'manager'
        }

    class SaEngineer(SaEmployee):
        __mapper_args__ = {
            'polymorphic_identity': 'engineer'
        }

    assert SaEmployee.__tablename__ == 'sa_employees'
    assert SaManager.__tablename__ == 'sa_employees'
    assert SaEngineer.__tablename__ == 'sa_employees'
    db.session.expunge_all()


def test_cti_custom_tablename():
    """Test Concrete Table Inheritance with a custom table name.
    """
    db = SQLAlchemy('sqlite://')

    class Person(db.Model):
        __tablename__ = 'cti_custom_people'
        id = db.Column(db.Integer, primary_key=True)
        name = db.Column(db.String(50))

    class Engineer(Person):
        __tablename__ = 'cti_custom_engineers'
        __mapper_args__ = {'concrete': True}
        id = db.Column(db.Integer, primary_key=True)
        primary_language = db.Column(db.String(50))
        name = db.Column(db.String(50))

    assert Person.__tablename__ == 'cti_custom_people'
    assert Engineer.__tablename__ == 'cti_custom_engineers'
    db.session.expunge_all()


def test_cti_auto_tablename():
    """Test Concrete Table Inheritance with an autonatically
    asigned table name.
    """
    db = SQLAlchemy('sqlite://')

    class Person(db.Model):
        id = db.Column(db.Integer, primary_key=True)
        name = db.Column(db.String(50))

    class Engineer(Person):
        __mapper_args__ = {'concrete': True}
        id = db.Column(db.Integer, primary_key=True)
        primary_language = db.Column(db.String(50))
        name = db.Column(db.String(50))

    class Teacher(Person):
        __tablename__ = 'cti_auto_teachers'
        __mapper_args__ = {'concrete': True}
        id = db.Column(db.Integer, primary_key=True)
        primary_language = db.Column(db.String(50))
        name = db.Column(db.String(50))

    assert Person.__tablename__ == 'people'
    assert Engineer.__tablename__ == 'engineers'
    assert Teacher.__tablename__ == 'cti_auto_teachers'
    db.session.expunge_all()


def test_acti_custom_tablename():
    """Test Abstract Concrete Table Inheritance with a custom table name.
    """
    db = SQLAlchemy('sqlite://')

    class Employee(AbstractConcreteBase, db.Model):
        pass

    class Manager(Employee):
        __tablename__ = 'acti_custom_managers'
        employee_id = db.Column(db.Integer, primary_key=True)
        name = db.Column(db.String(50))
        manager_data = db.Column(db.String(40))
        __mapper_args__ = {
            'polymorphic_identity': 'manager',
            'concrete': True
        }

    class Engineer(Employee):
        __tablename__ = 'acti_custom_engineers'
        employee_id = db.Column(db.Integer, primary_key=True)
        name = db.Column(db.String(50))
        engineer_info = db.Column(db.String(40))
        __mapper_args__ = {
            'polymorphic_identity': 'engineer',
            'concrete': True
        }

    assert Manager.__tablename__ == 'acti_custom_managers'
    assert Engineer.__tablename__ == 'acti_custom_engineers'
    db.session.expunge_all()


def test_acti_auto_tablename():
    """Test Abstract Concrete Table Inheritance with an autonatically
    asigned table name.
    """
    db = SQLAlchemy('sqlite://')

    class Employee(AbstractConcreteBase, db.Model):
        pass

    class Manager(Employee):
        __tablename__ = 'acti_auto_managers'
        employee_id = db.Column(db.Integer, primary_key=True)
        name = db.Column(db.String(50))
        manager_data = db.Column(db.String(40))
        __mapper_args__ = {
            'polymorphic_identity': 'manager',
            'concrete': True
        }

    class AaEngineer(Employee):
        employee_id = db.Column(db.Integer, primary_key=True)
        name = db.Column(db.String(50))
        engineer_info = db.Column(db.String(40))
        __mapper_args__ = {
            'polymorphic_identity': 'engineer',
            'concrete': True
        }

    assert Manager.__tablename__ == 'acti_auto_managers'
    assert AaEngineer.__tablename__ == 'aa_engineers'
    db.session.expunge_all()


def test_mixin_no_tablename():
    """Test for a tablename defined in a mixin.
    """
    db = SQLAlchemy('sqlite://')

    class BaseMixin(object):
        @declared_attr
        def id(cls):
            return db.Column(db.Integer, primary_key=True)

    class MEngineer(BaseMixin, db.Model):
        name = db.Column(db.String(50))

    assert MEngineer.__tablename__ == 'm_engineers'
    db.session.expunge_all()


def test_mixin_tablename():
    """Test for a tablename defined in a mixin.
    """
    db = SQLAlchemy('sqlite://')

    class EmployeeMixin(object):
        __tablename__ = 'mixin_tablename'

        @declared_attr
        def id(cls):
            return db.Column(db.Integer, primary_key=True)

    class Engineer(EmployeeMixin, db.Model):
        name = db.Column(db.String(50))

    assert Engineer.__tablename__ == 'mixin_tablename'
    db.session.expunge_all()


def test_mixin_overwritten_tablename():
    """Test for a tablename defined in a mixin but overwritten.
    """
    db = SQLAlchemy('sqlite://')

    class EmployeeMixin(object):
        __tablename__ = 'mixin_tablename'

        @declared_attr
        def id(cls):
            return db.Column(db.Integer, primary_key=True)

    class Engineer(EmployeeMixin, db.Model):
        __tablename__ = 'mixin_overwritten_tablename'
        name = db.Column(db.String(50))

    assert Engineer.__tablename__ == 'mixin_overwritten_tablename'
    db.session.expunge_all()


def test_declared_attr_mixin_tablename():
    """Test for a tablename defined as a @declared_attr in a mixin.
    """
    db = SQLAlchemy('sqlite://')

    class EmployeeMixin(object):
        @declared_attr
        def __tablename__(cls):
            return 'declared_attr_mixin_tablename'

        @declared_attr
        def id(cls):
            return db.Column(db.Integer, primary_key=True)

    class Engineer(EmployeeMixin, db.Model):
        name = db.Column(db.String(50))

    assert Engineer.__tablename__ == 'declared_attr_mixin_tablename'
    db.session.expunge_all()


def test_declared_attr_mixin_overwritten_tablename():
    """Test for a tablename defined as a @declared_attr in a mixin but overwritten
    """
    db = SQLAlchemy('sqlite://')

    class EmployeeMixin(object):
        @declared_attr
        def __tablename__(cls):
            return 'declared_attr_mixin_tablename'

        @declared_attr
        def id(cls):
            return db.Column(db.Integer, primary_key=True)

    class Engineer(EmployeeMixin, db.Model):
        __tablename__ = 'declared_attr_mixin_overwritten_engineers'
        name = db.Column(db.String(50))

    assert Engineer.__tablename__ == 'declared_attr_mixin_overwritten_engineers'
    db.session.expunge_all()
