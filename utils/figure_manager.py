class FigureManager:
    @staticmethod
    def get_figure_shapes():
        return {
            "corner": [(0, 0), (1, 0), (0, 1)],
            "corner_mirrored": [(0, 0), (0, 1), (1, 1)],
            "corner_rotated": [(0, 0), (1, 0), (1, 1)],
            "corner_rotated_mirrored": [(0, 0), (0, 1), (-1, 1)],
            "triangle_top_left": [(0, 0), (1, 0), (0, 1)],
            "triangle_top_right": [(0, 0), (1, 0), (1, 1)],
            "triangle_bottom_left": [(0, 0), (0, 1), (1, 1)],
            "triangle_bottom_right": [(1, 0), (0, 1), (1, 1)],
            "triangle_center_top": [(0, 0), (1, 0), (0.5, 0.5)],
            "triangle_center_right": [(1, 0), (1, 1), (0.5, 0.5)],
            "triangle_center_bottom": [(0, 1), (1, 1), (0.5, 0.5)],
            "triangle_center_left": [(0, 0), (0, 1), (0.5, 0.5)],
            "square": [(0, 0), (1, 0), (0, 1), (1, 1)]
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
    
    @staticmethod
    def get_triangle_shape_by_type(triangle_type):
        shapes = FigureManager.get_figure_shapes()
        if triangle_type == 0:
            return shapes["square"]
        elif triangle_type == 1:
            return shapes["triangle_top_left"]
        elif triangle_type == 2:
            return shapes["triangle_top_right"]
        elif triangle_type == 3:
            return shapes["triangle_bottom_left"]
        elif triangle_type == 4:
            return shapes["triangle_bottom_right"]
        elif triangle_type == 5:
            return shapes["triangle_center_top"]
        elif triangle_type == 6:
            return shapes["triangle_center_right"]
        elif triangle_type == 7:
            return shapes["triangle_center_bottom"]
        elif triangle_type == 8:
            return shapes["triangle_center_left"]
        else:
            return shapes["square"]