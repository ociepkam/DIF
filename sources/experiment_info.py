import datetime
from psychopy import gui


def experiment_info():
    """
    Dialog info shows at the beginning of the experiment.
    :return: part_id, part_sex, part_age, date
    """
    now = datetime.datetime.now()
    date = now.strftime("%Y-%m-%d %H:%M")

    my_dlg = gui.Dlg(title="DIF")
    my_dlg.addText('Subject info:')
    my_dlg.addField('Kod:')
    my_dlg.addField('Wiek:')
    my_dlg.addField('Plec:', choices=['M', "K"])

    my_dlg.show()
    if not my_dlg.OK:
        exit(1)

    #          id               sex             age
    return my_dlg.data[0], my_dlg.data[2], my_dlg.data[1], date
