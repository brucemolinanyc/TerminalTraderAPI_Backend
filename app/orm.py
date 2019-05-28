import sqlite3


class ORM:
    fields = []
    dbpath = "data/ttrader.db"
    tablename = ""

    def save(self):
        if self.pk is None:
            self._insert()
        else:
            self._update()

    def _insert(self):
        with sqlite3.connect(self.dbpath) as conn:
            curs = conn.cursor()
            fieldlist = ", ".join(self.fields)
            qmarks = ", ".join(["?" for _ in self.fields])

            SQL = """ INSERT INTO {tablename} ({fieldlist})
                      VALUES ({qmarks}); """.format(
                tablename=self.tablename, fieldlist=fieldlist, qmarks=qmarks)

            values = [getattr(self, field) for field in self.fields]
            curs.execute(SQL, values)

            self.pk = curs.lastrowid

    def _update(self):
        with sqlite3.connect(self.dbpath) as conn:
            curs = conn.cursor()
            assignments = ", ".join([
                "{} = ?".format(field) for field in self.fields])

            SQL = """ UPDATE {tablename} SET {assignments}
                      WHERE pk = ?; """.format(
                tablename=self.tablename, assignments=assignments)

            values = [getattr(self, field) for field in self.fields]
            values.append(self.pk)

            curs.execute(SQL, values)

    def delete(self):
        if not self.pk:
            raise KeyError(self.__repr__() +
                           " does not appear in the database")
        with sqlite3.connect(self.dbpath) as conn:
            curs = conn.cursor()
            SQL = """ DELETE FROM {tablename} WHERE pk = ?; """

            curs.execute(SQL, (self.pk, ))

    @classmethod
    def one_from_pk(cls, pk):
        result = cls.select_one_where("WHERE pk = ?", (pk, ))
        if not result:
            raise KeyError("no such pk: {}".format(pk))
        return result

    @classmethod
    def all(cls):
        return cls.select_many_where()

    @classmethod
    def select_one_where(cls, whereclause="", values=""):
        with sqlite3.connect(cls.dbpath) as conn:
            conn.row_factory = sqlite3.Row
            curs = conn.cursor()

            SQL = """ SELECT * FROM {tablename} {whereclause}; """.format(
                tablename=cls.tablename, whereclause=whereclause)

            curs.execute(SQL, values)
            result = curs.fetchone()
            if not result:
                return None
            return cls(**result)

    @classmethod
    def select_many_where(cls, whereclause="", values=""):
        with sqlite3.connect(cls.dbpath) as conn:
            conn.row_factory = sqlite3.Row
            curs = conn.cursor()

            SQL = """ SELECT * FROM {tablename} {whereclause}; """.format(
                tablename=cls.tablename, whereclause=whereclause)

            curs.execute(SQL, values)
            rows = curs.fetchall()
            return [cls(**row) for row in rows]
