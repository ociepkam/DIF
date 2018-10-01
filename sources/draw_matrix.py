from psychopy import visual


class TrialMatrix(object):
    """
    Simple stimuli aggregator. Behave like ordinal psychopy visual stimuli.
    """

    def __init__(self, matrix, position, window, viz_offset, text_size):
        self.position = position
        self.matrix = matrix
        self.stimulus_matrix = self._get_visual_stimulus(window=window, viz_offset=viz_offset, text_size=text_size)

    def set_auto_draw(self, draw):
        for stim in self.stimulus_matrix:
            stim.setAutoDraw(draw)

    def draw(self):
        for stim in self.stimulus_matrix:
            stim.draw()

    def _get_visual_stimulus(self, window, viz_offset, text_size):
        stimulus_matrix = list()
        for row_idx, row in enumerate(self.matrix.matrix):
            for cell_idx, cell in enumerate(row):
                x = cell_idx * viz_offset - viz_offset * (self.matrix.n-1)/2.0
                y = row_idx * viz_offset - viz_offset * (self.matrix.n-1)/2.0 + viz_offset
                stimulus = visual.TextStim(win=window, text=cell, color='black', height=text_size,pos=(x,y))
                stimulus_matrix.append(stimulus)
        return stimulus_matrix
