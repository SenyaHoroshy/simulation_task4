class FigureManager:
    @staticmethod
    def get_figure_shapes():
        return {
            "corner": [(0, 0), (1, 0), (0, 1)],
            "corner_mirrored": [(0, 0), (0, 1), (1, 1)],
            "corner_rotated": [(0, 0), (1, 0), (1, 1)],
            "corner_rotated_mirrored": [(0, 0), (0, 1), (-1, 1)]
        }
    
    @staticmethod
    def rotate_figure(figure, rotations=1):
        rotated = figure.copy()
        for _ in range(rotations % 4):
            rotated = [(y, -x) for x, y in rotated]
        return rotated
    
    @staticmethod
    def mirror_figure(figure):
        return [(-x, y) for x, y in figure]