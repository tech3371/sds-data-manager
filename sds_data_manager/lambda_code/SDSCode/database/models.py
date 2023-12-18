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
    spin_number = Column(Integer, nullable=False)
    spin_start_sc_time = Column(Integer, nullable=False)
    spin_start_utc_time = Column(DateTime(timezone=True), nullable=False)
    star_tracker_flag = Column(Boolean, nullable=False)
    spin_duration = Column(Integer, nullable=False)
    thruster_firing_event = Column(Boolean, nullable=False)
    repointing = Column(Boolean, nullable=False)
    repointing_number = Column(Integer, nullable=False)

    def __str__(self):
        """Returns a string representation of this object."""
        return "%s %s %d" % (self.directory_path, self.file_name, self.file_size)

    __repr__ = __str__
