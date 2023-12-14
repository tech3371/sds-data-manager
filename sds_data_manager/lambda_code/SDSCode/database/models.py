"""Main file to store schema definition"""
from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Integer,
)
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


class UniversalSpinTable(Base):
    """Universal Spin Table schema"""

    __tablename__ = "universal_spin_table"
    id = Column(Integer, primary_key=True)
    spin_number = Column(Integer, primary_key=True)
    spin_start_sc_time = Column(Integer)
    spin_start_utc_time = Column(DateTime(timezone=True))
    star_tracker_flag = Column(Boolean)
    spin_duration = Column(Integer)
    thruster_firing_event = Column(Boolean)
    repointing = Column(Boolean)
    repointing_number = Column(Integer)

    def __str__(self):
        """Returns a string representation of this object."""
        return "%s %s %d" % (self.directory_path, self.file_name, self.file_size)

    __repr__ = __str__
