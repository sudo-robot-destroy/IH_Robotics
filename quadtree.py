import math
import copy
import pygame
import numpy as np


class QuadTree(object):
    """An implementation of a quad-tree.

    Acknowledgements:
    [1] http://mu.arete.cc/pcr/syntax/quadtree/1/quadtree.py
    """
    def __init__(self, items, depth, bounding_rect=None):
        """Creates a quad-tree.

        @param items:
            A sequence of items to store in the quad-tree.

        @param depth:
            The maximum recursion depth.

        @param bounding_rect:
            The bounding rectangle of all of the items in the quad-tree. For
            internal use only.
        """
        # The sub-quadrants are empty to start with.
        self.nw = self.ne = self.se = self.sw = None

        # Find this quadrant's centre.
        if bounding_rect:
            l, t, r, b = bounding_rect
        else:
            # If there isn't a bounding rect, then calculate it from the items.
            l = min(item.X for item in items)
            t = min(item.Y for item in items)
            r = max(item.X for item in items)
            b = max(item.Y for item in items)
        cx = (l + r) * 0.5
        cy = (t + b) * 0.5

        self.vert_start_pos = (cx, cy + 0.5*(b - t))
        self.vert_end_pos = (cx, cy - 0.5*(b - t))

        self.horz_start_pos = (cx + 0.5*(r-l), cy)
        self.horz_end_pos = (cx - 0.5*(r-l), cy)

        # If we've reached the maximum depth then insert all items into this
        # quadrant.
        depth -= 1
        if depth == 0:
            self.items = items
            return

        self.items = []
        nw_items = []
        ne_items = []
        se_items = []
        sw_items = []

        for item in items:
            # Which of the sub-quadrants does the item overlap?
            in_nw = item.X <= cx and item.Y <= cy
            in_sw = item.X <= cx and item.Y >= cy
            in_ne = item.X >= cx and item.Y <= cy
            in_se = item.X >= cx and item.Y >= cy

            # If it overlaps all 4 quadrants then insert it at the current
            # depth, otherwise append it to a list to be inserted under every
            # quadrant that it overlaps.
            if in_nw and in_ne and in_se and in_sw:
                self.items.append(item)
            else:
                if in_nw:
                    nw_items.append(item)
                if in_ne:
                    ne_items.append(item)
                if in_se:
                    se_items.append(item)
                if in_sw:
                    sw_items.append(item)

        # Create the sub-quadrants, recursively.
        if nw_items:
            self.nw = QuadTree(nw_items, depth, (l, t, cx, cy))
        if ne_items:
            self.ne = QuadTree(ne_items, depth, (cx, t, r, cy))
        if se_items:
            self.se = QuadTree(se_items, depth, (cx, cy, r, b))
        if sw_items:
            self.sw = QuadTree(sw_items, depth, (l, cy, cx, b))

    def plotTree(self, node):
        drawSquare(node, (0, 0, 255))
        if node.ne is not None:
            self.plotTree(node.ne)
        if node.nw is not None:
            self.plotTree(node.nw)
        if node.se is not None:
            self.plotTree(node.se)
        if node.sw is not None:
            self.plotTree(node.sw)


def rectangle(width, height, center, theta, WIDTH, HEIGHT):
    points = []
    for i in np.linspace(0, 2*math.pi, 300):
        x = width/2*(abs(np.cos(i))*np.cos(i) + abs(np.sin(i))*np.sin(i))
        y = height/2*(abs(np.cos(i))*np.cos(i) - abs(np.sin(i))*np.sin(i))
        rot = np.array([[np.cos(theta), np.sin(theta)],
                        [-np.sin(theta), np.cos(theta)]])
        rotated = np.dot(rot, np.array([[x], [y]]))
        rotated[0] += center[0]
        rotated[1] += center[1]

        if (rotated[0] > 0) and (rotated[0] < WIDTH) and\
           (rotated[1] > 0) and (rotated[1] < HEIGHT):
            points.append(Point(rotated[0], rotated[1]))
    return points


# The class that we're storing in the quad-tree. It possesses the necessary
# attributes of left, top, right and bottom, and it is hashable.
class Point(object):
    def __init__(self, X, Y):
        self.X = X
        self.Y = Y

    def draw(self):
        pygame.draw.circle(screen, (255, 255, 255), [self.X, self.Y], 0)


def drawSquare(node, color):
    pygame.draw.line(screen, color, node.vert_start_pos, node.vert_end_pos)
    pygame.draw.line(screen, color, node.horz_start_pos, node.horz_end_pos)


def drawRecursive(node, color):
    drawSquare(node, color)
    if node.ne is not None:
        drawRecursive(node.ne, color)
    if node.nw is not None:
        drawRecursive(node.nw, color)
    if node.se is not None:
        drawRecursive(node.se, color)
    if node.sw is not None:
        drawRecursive(node.sw, color)


def compareTreesRecursive(tree1, tree2):
    # see if any nodes were removed or added
    if tree1.ne is not None and tree2.ne is None:
        drawRecursive(tree1.ne, (255, 0, 0))
    elif tree1.ne is None and tree2.ne is not None:
        drawRecursive(tree2.ne, (0, 255, 0))
    elif tree1.ne is not None and tree2.ne is not None:
        compareTreesRecursive(tree1.ne, tree2.ne)

    if tree1.nw is not None and tree2.nw is None:
        drawRecursive(tree1.nw, (255, 0, 0))
    elif tree1.nw is None and tree2.nw is not None:
        drawRecursive(tree2.nw, (0, 255, 0))
    elif tree1.nw is not None and tree2.nw is not None:
        compareTreesRecursive(tree1.nw, tree2.nw)

    if tree1.se is not None and tree2.se is None:
        drawRecursive(tree1.se, (255, 0, 0))
    elif tree1.se is None and tree2.se is not None:
        drawRecursive(tree2.se, (0, 255, 0))
    elif tree1.se is not None and tree2.se is not None:
        compareTreesRecursive(tree1.se, tree2.se)

    if tree1.sw is not None and tree2.sw is None:
        drawRecursive(tree1.sw, (255, 0, 0))
    elif tree1.sw is None and tree2.sw is not None:
        drawRecursive(tree2.sw, (0, 255, 0))
    elif tree1.sw is not None and tree2.sw is not None:
        compareTreesRecursive(tree1.sw, tree2.sw)


def drawLeaf(node, color):
    nodeIsEmpty = True
    if node.ne is not None:
        drawLeaf(node.ne, color)
        nodeIsEmpty = False
    if node.nw is not None:
        drawLeaf(node.nw, color)
        nodeIsEmpty = False
    if node.se is not None:
        drawLeaf(node.se, color)
        nodeIsEmpty = False
    if node.sw is not None:
        drawLeaf(node.sw, color)
        nodeIsEmpty = False
    if nodeIsEmpty:
        drawSquare(node, color)


def compareTreeLeaves(tree1, tree2):
    # see if any nodes were removed or added
    if tree1.ne is not None and tree2.ne is None:
        drawLeaf(tree1.ne, (255, 0, 0))
    elif tree1.ne is None and tree2.ne is not None:
        drawLeaf(tree2.ne, (0, 255, 0))
    elif tree1.ne is not None and tree2.ne is not None:
        compareTreeLeaves(tree1.ne, tree2.ne)

    if tree1.nw is not None and tree2.nw is None:
        drawLeaf(tree1.nw, (255, 0, 0))
    elif tree1.nw is None and tree2.nw is not None:
        drawLeaf(tree2.nw, (0, 255, 0))
    elif tree1.nw is not None and tree2.nw is not None:
        compareTreeLeaves(tree1.nw, tree2.nw)

    if tree1.se is not None and tree2.se is None:
        drawLeaf(tree1.se, (255, 0, 0))
    elif tree1.se is None and tree2.se is not None:
        drawLeaf(tree2.se, (0, 255, 0))
    elif tree1.se is not None and tree2.se is not None:
        compareTreeLeaves(tree1.se, tree2.se)

    if tree1.sw is not None and tree2.sw is None:
        drawLeaf(tree1.sw, (255, 0, 0))
    elif tree1.sw is None and tree2.sw is not None:
        drawLeaf(tree2.sw, (0, 255, 0))
    elif tree1.sw is not None and tree2.sw is not None:
        compareTreeLeaves(tree1.sw, tree2.sw)


def plotShape(shape):
    for item in shape:
        item.draw()


if __name__ == '__main__':

    print("Move shape with directional arrows\n\
Rotate shape:\nZ counterclockwise\nX clockwise\n\n\
Resize shape:\nA narrower\nD wider \nW taller\nS shorter\n\n\
Change tree depth:\n+ Increase\n- Decrease\n\n\
Q Hide/Show Quadtree\n\
E Hide/Show Changetree\n\
C Hide/Show Points\n\
R Display Changetree recursively or just the leaf nodes")
    HEIGHT = 900    # HEIGHT of quadtree
    WIDTH = HEIGHT  # WIDTH of quadtree
    tree_depth = 9
    width = 50      # width of rectangle
    height = 100    # height of rectangle
    angle = 0       # rotation of rectangle
    cent = np.array([WIDTH/2.0, HEIGHT/2.0])
    shape = rectangle(width, height, (cent), angle, WIDTH, HEIGHT)

    screen = pygame.display.set_mode((int(WIDTH), int(HEIGHT)),
                                     pygame.DOUBLEBUF)
    screen.fill((0, 0, 0))
    # Put them into a quad-tree.
    tree = QuadTree(shape, tree_depth, (0, 0, WIDTH, HEIGHT))
    tree.plotTree(tree)
    plotShape(shape)
    pygame.display.flip()
    pygame.key.set_repeat(100)
    stop = False
    showPoints = True
    showQuadtree = True
    showChangetree = True
    doRecursiveChangeTreeDisp = False
    while not stop:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                stop = True
            elif event.type == pygame.KEYDOWN:
                screen.fill((0, 0, 0))
                items = []
                if event.key == pygame.K_ESCAPE:
                    stop = True
                elif event.key == pygame.K_UP:
                    cent[1] -= 10
                    print("center = " + repr(cent))
                elif event.key == pygame.K_DOWN:
                    cent[1] += 10
                    print("center = " + repr(cent))
                elif event.key == pygame.K_RIGHT:
                    cent[0] += 10
                    print("center = " + repr(cent))
                elif event.key == pygame.K_LEFT:
                    cent[0] -= 10
                    print("center = " + repr(cent))
                elif event.key == pygame.K_a:
                    width -= 10
                    print("size = " + repr(height) + " x " + repr(width))
                elif event.key == pygame.K_d:
                    width += 10
                    print("size = " + repr(height) + " x " + repr(width))
                elif event.key == pygame.K_w:
                    height += 10
                    print("size = " + repr(height) + " x " + repr(width))
                elif event.key == pygame.K_s:
                    height -= 10
                    print("size = " + repr(height) + " x " + repr(width))
                elif event.key == pygame.K_KP_PLUS:
                    tree_depth += 1
                    print("depth = " + repr(tree_depth))
                elif event.key == pygame.K_KP_MINUS:
                    if tree_depth > 1:
                        tree_depth -= 1
                    print("depth = " + repr(tree_depth))
                elif event.key == pygame.K_z:
                    angle += 0.05
                    print("angle = " + repr(angle))
                elif event.key == pygame.K_x:
                    angle -= 0.05
                    print("angle = " + repr(angle))
                elif event.key == pygame.K_q:
                    showQuadtree = not showQuadtree
                    print("Toggled display of quadtree")
                elif event.key == pygame.K_e:
                    showChangetree = not showChangetree
                    print("Toggled display of changetree")
                elif event.key == pygame.K_c:
                    showPoints = not showPoints
                    print("Toggled display of points")
                elif event.key == pygame.K_r:
                    doRecursiveChangeTreeDisp = not doRecursiveChangeTreeDisp
                    print("Toggled how change tree is displayed")

                shape = rectangle(width, height, cent, angle, WIDTH, HEIGHT)
                oldTree = copy.copy(tree)
                tree = QuadTree(shape, tree_depth, (0, 0, WIDTH, HEIGHT))

                if showQuadtree:
                    tree.plotTree(tree)
                if showChangetree:
                    if doRecursiveChangeTreeDisp:
                        compareTreesRecursive(oldTree, tree)
                    else:
                        compareTreeLeaves(oldTree, tree)
                if showPoints:
                    plotShape(shape)

                pygame.display.flip()
    pygame.quit()
