from can_source.can_libs.lib_gobals import define_func


def cantonese_csv_init() -> None:
    import csv

    @define_func("睇睇csv有咩")
    def out_csv_read(file):
        for i in csv.reader(file):
            print(i)

    @define_func("讀取csv")
    def get_csv(file):
        ret = []
        for i in csv.reader(file):
            ret.append(i)
        return i
