import pygame
import random
import sys
from tkinter import messagebox

# Permet d'initialiser un bouton
class Button:
    # Constructeur de la classe bouton
    # x: int            la position en x du bouton
    # y: int            la position en y du bouton
    # size: int         la longueur d'un côté du bouton
    # bomb: bool        vrai si le bouton contient une bombe
    # square: int       l'index du bouton dans la grille
    def __init__(self, x, y, size, bomb, square):
        self.bomb = bomb
        self.clicked = False
        self.flag = 0
        self.is_checked = False
        self.is_ai_looked = False
        self.bombs_around = 0
        self.square_value = square
        self.x = x + 2
        self.y = y + 2
        self.square_size = size
        self.center = (self.x + size / 2, self.y + size / 2)
        self.size = (size, size)
        self.surface = pygame.Surface(self.size)
        self.surface.fill(dark_grey)
        self.rect = pygame.draw.rect(screen, red, pygame.Rect(x, y, size + 4, size + 4),  2)
    # Vérifie si c'est le premier clic de la partie et si c'est un mauvais depart
    # bon depart: lorsqu'il n'y a pas de bombes sur la case et aucune bombes autour de la première case cliquée
    # Return: Vrai s'il faut continuer avec le reste du code, faux (mauvais depart)
    def firstClickCheck(self):
        next = True
        if game_controller.firstClick:
            if self.bomb or self.bombs_around != 0:
                next = False
                game_controller.restartFirstClick(self)
        return next
    # Ce qui se passe lorsqu'un clic droit est appliqué sur le bouton
    def rightClick(self):
        input = [[-1, flag_image], [1, self.surface]]
        self.rightClickFlag(input[self.flag][0], input[self.flag][1])
        self.flag = (self.flag + 1) % 2
        self.is_ai_looked = not self.is_ai_looked
        showText(str(game_controller.number_of_flag_left), (game_controller.screen_size[0]-50, 20), light_grey, (40, 40))
    # Affiche la bonne surface et le bon increment selon les paramètres
    # increment: int            L'incrément à ajouter au nombre de drapeaux restants
    # surface: Surface          La surface à afficher
    def rightClickFlag(self, increment, surface):
        showImage(surface, self.center, self.size)
        game_controller.number_of_flag_left += increment
    # Ce qui se passe lorsqu'un clic gauche est appliqué sur le bouton
    def leftClick(self):
        if not self.clicked and not self.flag and self.firstClickCheck():
            if self.bomb: 
                showImage(bomb_image, self.center, self.size)
                game_controller.gameLose()
            else:
                self.clicked = True
                game_controller.firstClick = False
                game_controller.timer_start = True
                game_controller.square_clicked += 1
                text = " "
                if self.bombs_around != 0:
                    text = str(self.bombs_around)
                showText(text, (self.x + self.square_size / 2, self.y + self.square_size / 2), light_grey, self.size)
                if self.bombs_around == 0:
                    self.is_ai_looked = True
                    game_controller.grid.recursiveZero(self)
                game_controller.gameWin()
# Permet d'intialiser une grille de jeu pour la partie
class Grid:
    # Constructeur du la classe
    # len_x: int            le nombre de cases en x (gauche à droite)
    # len_y: int            le nombre de cases en y (haut en bas)
    # button_size: int      la longueur d'un côté de bouton
    # number_of_bombs: int  le nombre de bombes dans la grille
    def __init__(self, len_x, len_y, button_size, number_of_bombs):
        self.len_x = len_x
        self.len_y = len_y
        self.area = len_x * len_y
        self.bombs = self.generateBombs(number_of_bombs)
        self.button_list = self.generateButtons(button_size)
        self.bombsAround()
    # Génère le nombre de bombes requises au niveau
    # number_of_bombs: int      Le nombre de bombes à générer pour la partie
    # return: int[]             Un tableau avec l'index des bombes dans le niveau
    def generateBombs(self, number_of_bombs):
        index = 0
        bombs = []
        while index < number_of_bombs:
            random_value = random.randint(0, self.area-1)
            if random_value not in bombs:
                bombs.append(random_value)
                index += 1
        return bombs
    # Génère le nombre de boutons requis au niveau
    # button_size: int          La longueur d'un côté de la case
    # return: Button[]          Un tableau contenant toutes les cases de la grille de jeu
    def generateButtons(self, button_size):
        index = 0
        button_list = []
        for i in range(self.len_x):
            for j in range(self.len_y):
                bomb = False
                if index in self.bombs:
                    bomb = True
                button_list.append(Button(i*(button_size + 4), j*(button_size + 4) + 40, button_size, bomb, index))
                index += 1
        return button_list
    # Pour chaque bombes dans la liste, ajoute 1 au compteur de bombe à toutes les cases autour
    def bombsAround(self):
        for bomb in self.bombs:
            addition = self.getAddition(bomb)
            for add in addition:
                self.button_list[bomb + add].bombs_around += 1
    # Retourne le bouton de la liste qui est au coordonnées données
    # return: Button            Le bouton qui est aux coordonnées du clic de souris
    def getButton(self, x, y):
        for button in self.button_list:
            if button.rect.collidepoint(x, y):
                return button
    # Déclenche une recursivité de clic si le bouton cliqué n'a pas de bombes autour
    # Mécanique présente dans le jeu
    # button: Button        Le bouton qui exécute la recursivité (il a 0 bombes autour de lui)
    def recursiveZero(self, button):
        if not button.is_checked:
            addition = self.getAddition(button.square_value)
            for add in addition:
                if self.button_list[int(button.square_value) + add].bombs_around != 0:
                    self.button_list[int(button.square_value) + add].is_checked = True
                self.button_list[int(button.square_value) + add].leftClick()
    # Retourne un tableau avec l'incrément pour accèder aux cases autour d'un index
    # square_value: int     L'index dont on veut avoir les cases autour
    # return: int[]         un tableau avec les incréments pour accèder aux cases autour de l'index
    #
    #   0 1 2
    #   7 x 3
    #   6 5 4 
    #
    # Comment calculer l'index des cases autours
    # len_y: le nombre de cases en y de la grille
    # x: l'index de la case
    # 0: -1-len_y
    # 1: -1
    # 2: +len_y-1
    # 3: +len_y
    # 4: +len_y+1
    # 5: +1
    # 6: 1-len_y
    # 7: -len_y
    def getAddition(self, square_value):
        addition = [-1-self.len_y, -1, self.len_y-1, self.len_y, self.len_y+1, 1, 1-self.len_y, -self.len_y]
        index_remove = []
        # Ajoute un tableau avec les index à enlever du tableau addition
        if self.len_y > square_value >= 0:
            index_remove.append([0, 7, 6])
        if self.area > square_value >= self.area - self.len_y:
            index_remove.append([2, 3, 4])
        if square_value % self.len_y == 0:
            index_remove.append([0, 1, 2])
        if square_value % self.len_y == self.len_y-1:
            index_remove.append([4, 5, 6])
        # Faire en sorte que ce soit juste un tableau de int
        # et non un tableau de tableau de int
        # int[][] --> int[]
        flat_index_remove = []
        for row in index_remove:
            flat_index_remove.extend(row)
        # enlève les index en double
        flat_index_remove = list(set(flat_index_remove))
        flat_index_remove.sort(reverse=True)
        # Enlève les index du tableau d'addition
        for index in flat_index_remove:
            addition.pop(index)
        return addition
# S'occupe de la gestion de la partie
class GameController:
    # Constructeur du gestionnaire de partie
    # Défini les caracteristiques de base de la partie
    # level: int    Le niveau de difficulté de la partie
    def __init__(self, level):
        self.level = level
        screen = pygame.display.set_mode((difficulties[level].screen_size_x, difficulties[level].screen_size_y))
        screen.fill(dark_grey)
        self.screen_size = [difficulties[level].screen_size_x, difficulties[level].screen_size_y]
        self.time_elapsed = 0
        self.grid = Grid(difficulties[level].len_x, difficulties[level].len_y, difficulties[level].square_size, difficulties[level].number_of_bombs)
        self.number_of_bombs = difficulties[level].number_of_bombs
        self.difficulty_button_list = []
        self.number_of_flag_left = self.number_of_bombs
        self.square_clicked = 0
        self.firstClick = True
        self.end = False
        self.timer_start = False
        self.restart_button = showText("Recommencer", (100, 20), light_grey, (200, 40))
        self.ai_help_button = showText("IA", (350, 20), light_grey, (50, 40))
        showText(str(self.number_of_bombs), (difficulties[level].screen_size_x-50, 20), light_grey, (40, 40))
        showImage(flag_image, (difficulties[level].screen_size_x-100, 20), (40, 40))
    # Affiche la page principale pour la sélection du niveau de difficulté
    def showMainScreen(self):
        self.end = True
        screen = pygame.display.set_mode((1000, 700))
        screen.fill(dark_grey)
        pos = 275
        showText("Choisissez votre difficulté", (500, 100), dark_grey, None)
        for difficulty in difficulties:
            textRect = showText(difficulty.name, (500, pos), light_grey, None)
            self.difficulty_button_list.append(textRect)
            pos += 125
    # Vérifie et gère la victoire de la partie
    def gameWin(self):
        if self.square_clicked == self.grid.area - self.number_of_bombs:
            self.timer_start = False
            messagebox.showinfo('Vous avez gagné', 'Vous avez gagné en ' + str(game_controller.time_elapsed) + ' secondes')
    # Gère la defaite de la partie
    def gameLose(self):
        if self.timer_start:
            self.timer_start = False
            for bomb in self.grid.bombs:
                self.grid.button_list[bomb].leftClick()
            for button in self.grid.button_list:
                if button.flag and not button.bomb:
                    showImage(incorrect_flag_image, button.center, button.size)
                button.clicked = True
    # Recommence la partie si c'est un départ incorrect
    # Pour avoir une bon depart, il faut qu'il y aie 0 bombes autour de la première case cliquée
    def restartFirstClick(self, button):
        self.grid = Grid(self.grid.len_x, self.grid.len_y, self.grid.button_list[0].square_size, self.number_of_bombs)
        new_button = self.grid.getButton(button.x, button.y)
        new_button.leftClick()
    # Gère l'affichage du timer
    def updateTimer(self):
        if not self.firstClick and self.timer_start:
            self.time_elapsed += 1
            showText(str(self.time_elapsed), (self.screen_size[0] / 2, 20), light_grey, (50, 40))
    # Gère quoi faire lors d'un clic de souris
    # event: Event      L'évènement qui contient quel bouton de la souris a été appuyé
    def onClick(self, event):
        x, y = pygame.mouse.get_pos()
        button = self.grid.getButton(x, y)
        if button is None:
            # clic bouton recommencer
            if self.restart_button.collidepoint(x, y):
                self.showMainScreen()
                self.timer_start = False
            # clic bouton aide ia
            if self.ai_help_button.collidepoint(x, y):
                game_ai.stop = not game_ai.stop
        if isinstance(button, Button):
            if not button.clicked:
                if event.button == 1:
                    button.leftClick()
                elif event.button == 3:
                    button.rightClick()
    # Gère quel niveau de difficulté est choisi
    def onChooseDifficulty(self):
        x, y = pygame.mouse.get_pos()
        index = 0
        game_ai.stop = True
        for difficulty in self.difficulty_button_list:
            if difficulty.collidepoint(x, y):
                self.__init__(index)
            index += 1
# Une intelligence artificielle qui connait les mes informations qu'un humain pourrait voir sur la grille de jeu
# et qui suit une série de règles prédéfinies pour déterminer les coups à faire sur la grille
class GameAi:
    def __init__(self):
        self.stop = True
        self.grid = game_controller.grid
    # Va chercher la grille de jeu dans le controleur de jeu
    def getGrid(self):
        self.grid = game_controller.grid
    # Trouve une case possible selon la vérification et effectue le clic en fonction des paramètres
    # function_name_check: string       la fonction de clic qui est utilisé pour trouver une case
    # function_name_execute: string     la fonction qui execute un clic sur la grille
    # condition: string                 la fonction qui vérifie une condition pour le clic
    # return: bool                      vrai si la fonction a executé un clic, faux sinon
    def doOneMoveFunction(self, function_name_check, function_name_execute, condition=None):
        found = False
        for button in self.grid.button_list:
            # regarde tous les cases qui n'ont pas déjà été vérifiés et qui ont été cliquées
            # les cases cliquées sont les cases visibles sur la grille de jeu
            if not found and not button.is_ai_looked and button.clicked:
                # regarde les types de clic qui peuvent être effectuées autour de cette case
                function_check = getattr(game_ai, function_name_check)
                square_to_click = function_check(button, condition)
                if square_to_click != -1:
                    found = True
        # si une case a été trouvée, effectue l'action du clic
        if found:
            click = getattr(game_ai.grid.button_list[square_to_click], function_name_execute)
            click()
        return found
    # trouve un coup à faire (clic droit ou gauche)
    def doOneMove(self):
        self.getGrid()
        # règle #1
        if not self.doOneMoveFunction("rightClickRule", "rightClick"):
            # règle #2
            if not self.doOneMoveFunction("leftClickRule", "leftClick"):
                # règle #3
                if not self.doOneMoveFunction("checkBombSafeRule", "leftClick", "checkConditionSafeRule"):
                    # règle #4
                    if not self.doOneMoveFunction("checkBombSafeRule", "rightClick", "checkConditionBombRule"):
                        self.flipACoinOneMove()
                        # pour l'instant, il y a seulement ces quatres règles d'implémentées,
                        # mais d'autre règles pourraient être implémentées pour donner la chance
                        # à l'ia de savoir quoi faire dans plus de cas
                        self.stop = True
    # Regarde s'il reste seulement deux cases possibles et une bombe sur la grille
    # Sélectionne une des deux cases possibles et fait un clic gauche dessus
    # Cette règle est seulement déclenchée lorsque plus aucun coup n'est possible avec les autre règles
    def flipACoinOneMove(self):
        index_square_left = []
        for button in self.grid.button_list:
            if self.checkNotClickedNotFlag(button.square_value):
                index_square_left.append(button.square_value)
        if len(index_square_left) == 2 and game_controller.number_of_flag_left == 1:
            self.grid.button_list[index_square_left[0]].leftClick()
    # Regarde autour d'une case si un clic droit peut être fait (mettre un drapeau)
    # En bref, la fonction regarde s'il reste autant de bombes autour de la case que 
    # de case non-cliquées
    # button: Button            la case centrale (on vérifie toutes les cases autour de celle-ci)
    # condition: None           N'est pas utile pour cette fonction
    # return: int               retourne l'index de la case à cliquer
    def rightClickRule(self, button, condition):
        square_to_click = -1
        addition = self.grid.getAddition(button.square_value)
        squares_left = len(self.getArrayRemainingSquares(button.square_value, addition))
        flags_left = self.getNumberFlagsAroundLeft(button.square_value, addition)
        if flags_left == squares_left:
            for add in addition:
                if self.checkNotClickedNotFlag(button.square_value + add):
                    square_to_click = button.square_value + add
        return square_to_click
    # Regarde autour d'une case si un clic gauche peut être fait
    # En bref, la fonction regarde s'il y a autant de bombes autour de la case centrale
    # que de drapeaux. S'il y a autant des deux, ça veut dire que toutes les autres cases sont safe
    # button: Button            la case centrale (on vérifie toutes les cases autour de celle-ci)
    # condition: None           n'est pas utile pour cette fonction
    # return: int               retourne l'index de la case à cliquer
    def leftClickRule(self, button, condition):
        square_to_click = -1
        addition = self.grid.getAddition(button.square_value)
        flags_around = self.getNumberFlagsAround(button.square_value, addition)
        if button.bombs_around == flags_around:
            for add in addition:
                if self.checkNotClickedNotFlag(button.square_value + add):
                    square_to_click = button.square_value + add
        return square_to_click
    # Cette fonction est utile pour les règles 3 et 4
    # Elle regarde si la case passée en paramètres manque un drapeau et à deux cases restantes
    # Si oui, elle va chercher les cases voisines et effectue la condition passée en paramètres
    # button: Button            La case principale
    # condition: string         la fonction qui vérifie une condition pour le clic
    def checkBombSafeRule(self, button, condition):
        square_to_click = -1
        addition = self.grid.getAddition(button.square_value)
        flags_left_around_main = self.getNumberFlagsAroundLeft(button.square_value, addition)
        array_index_square_left_main = self.getArrayRemainingSquares(button.square_value, addition)
        # si la case de base manque 1 drapeau et à deux cases restantes
        if flags_left_around_main == 1 and len(array_index_square_left_main) == 2:
            for add in addition:
                # additions haut, bas, gauche et droite
                if add == 1 or add == -1 or add == self.grid.len_y or add == -self.grid.len_y:
                    neighboor_square = button.square_value + add
                    # Il faut que les deux conditions soient vraies pour que la case soit visible sur la grille
                    if not self.checkFlag(neighboor_square) and self.checkClicked(neighboor_square):
                        neighboor_square_addition = self.grid.getAddition(neighboor_square)
                        flags_left_around_neighboor = self.getNumberFlagsAroundLeft(neighboor_square, neighboor_square_addition)
                        array_index_square_left_neighboor = self.getArrayRemainingSquares(neighboor_square, neighboor_square_addition)
                        # vérifie la condition passée en paramètres
                        checkCondition = getattr(game_ai, condition)
                        if checkCondition(flags_left_around_neighboor, array_index_square_left_neighboor):
                            goodPosition = True
                            for square in array_index_square_left_main:
                                try:
                                    array_index_square_left_neighboor.remove(square)
                                except:
                                    goodPosition = False
                            if goodPosition:
                                square_to_click = array_index_square_left_neighboor[0]
        return square_to_click  
    # Regarde si une case n'est pas cliquée et qu'il n'y a pas de drapeau dessus
    # square: int       l'index de la case à vérifier
    # return: bool      vrai si la case n'est pas cliquée et qu'elle n'a pas de drapeau, faux sinon
    def checkNotClickedNotFlag(self, square):
        return not self.checkClicked(square) and not self.checkFlag(square)
    # Regarde si une case est cliquée
    # square: int       l'index de la case à vérifier
    # return: bool      vrai si la case est cliquée, faux sinon
    def checkClicked(self, square):
        return self.grid.button_list[square].clicked
    # Regarde si une case a une drapeau dessus
    # square: int       l'index de la case à vérifier
    # return: bool      vrai si la case a un drapeau dessus, faux sinon
    def checkFlag(self, square):
        return self.grid.button_list[square].flag
    # Regarde le nombre de drapeaux autour d'une case
    # square: int       l'index de la case à vérifier
    # addition: int[]   un tableau contenant les additions à effectuer pour obtenir l'index des cases autour de la case principale
    # return: int       le nombre de cases autour de la case à vérifier
    def getNumberFlagsAround(self, square, addition):
        flags_around = 0
        for add in addition:
            if self.checkFlag(square + add):
                flags_around += 1
        return flags_around
    # Regarde les cases pouvant être cliquées autour d'une case
    # square: int       l'index de la case à vérifier
    # addition: int[]   un tableau contenant les additions à effectuer pour obtenir l'index des cases autour de la case passée en paramètre
    # return: int[]     un tableau contenant l'index de toutes les cases pouvant être cliquées
    def getArrayRemainingSquares(self, square, addition):
        array_index_remaining_squares = []
        for add in addition:
            if self.checkNotClickedNotFlag(square + add):
                array_index_remaining_squares.append(square + add)
        return array_index_remaining_squares
    # Regarde le nombre de drapeaux manquants autour d'une case
    # square: int       l'index de la case à vérifier
    # addition: int[]   un tableau contenant les additions à effectuer pour obtenir l'index des cases autour de la case passée en paramètre
    # return: int       le nombre de drapeaux restants à mettre autour de la case passée en paramètre
    def getNumberFlagsAroundLeft(self, square, addition):
        return self.grid.button_list[square].bombs_around - self.getNumberFlagsAround(square, addition)
    # Exemple de situation de jeu:
    #   @ @ @ @ @       @ @ @ @ @
    #   . X . . @       . X . . @
    #   . X 4 1 @       . 2 2 1 @
    #   . X 2 0 @       . 2 0 0 @
    #   . . 2 0 @       . 2 0 0 @
    #   
    #   @ : pas une case, c'est en dehors de la grille de jeu
    #   . : une case qui n'a pas encore été devoilée
    #   X : une case qui n'a pas encore été devoilée, mais on sait que c'est une bombe grace à cette règle
    # Explication:
    # Cette fonction prend une case, cette case doit avoir qu'une seule bombe restante et deux case possibles
    # La fonction regarde la case à gauche, droit, en haut et en bas de la case initiale.
    # Si cette case (la case adjacente à la case centrale) a autant de bombes restantes + 1 que de cases restantes,
    # on peut déterminer que toutes les cases qui ne font pas partie des deux cases initialement possibles sont des bombes
    # flags_left_around_neighboor: int              Le nombre de drapeaux restants à mettre autour de la case voisine
    # array_index_square_left_neighboor: int[]      un tableau contenant l'index des cases pouvant être appuyées autour de la case voisine
    # return: bool                                  Vrai si la condition de cette règle est valide, faux sinon
    def checkConditionBombRule(self, flags_left_around_neighboor, array_index_square_left_neighboor):
        if flags_left_around_neighboor + 1 == len(array_index_square_left_neighboor) and len(array_index_square_left_neighboor) > 2:
            return True
        return False
    # Exemple de situation de jeu:
    #   @ @ @ @ @
    #   . X . . @
    #   . X 1 1 @
    #   . X 1 0 @  
    #   
    #   @ : pas une case, c'est en dehors de la grille de jeu
    #   . : une case qui n'a pas encore été devoilée
    #   X : une case qui n'a pas encore été devoilée, mais on sait qu'elle est safe grâce à cette règle
    # Explication:
    # Cette fonction prend une case, cette case doit avoir qu'une seule bombe restante et deux case possibles
    # La fonction regarde la case à gauche, droit, en haut et en bas de la case initiale.
    # Si cette case (la case adjacente à la case centrale) a une seule bombe restante et trois cases ou plus possibles,
    # on peut determiner que toutes les cases qui ne font pas partie des deux cases initialement possibles sont safe
    # flags_left_around_neighboor: int              Le nombre de drapeaux restants à mettre autour de la case voisine
    # array_index_square_left_neighboor: int[]      un tableau contenant l'index des cases pouvant être appuyées autour de la case voisine
    # return: bool                                  Vrai si la condition de cette règle est valide, faux sinon
    def checkConditionSafeRule(self, flags_left_around_neighboor, array_index_square_left_neighboor):
        if flags_left_around_neighboor == 1 and len(array_index_square_left_neighboor) > 2:
            return True
        return False
# Gère les informations de difficulté
# number_of_bombs: int      le nombre de bombes
# len_x: int                le nombre de cases en x (gauche à droite)
# len_y: int                le nombre de cases en y (haut en bas)
# square_size: int          la longueur d'un côté d'une case
# screen_size_x: int        la longueur de la fenetre en x (gauche à droite)
# screen_size_y: int        la longueur de la fenetre en y (haut en bas)
class Difficulty:
    def __init__(self, name, number_of_bombs, len_x, len_y, square_size, screen_size_x, screen_size_y):
        self.number_of_bombs = number_of_bombs
        self.len_x = len_x
        self.len_y = len_y
        self.square_size = square_size
        self.screen_size_x = screen_size_x
        self.screen_size_y = screen_size_y
        self.name = name
# Affiche un texte à une certaine position
# text: String                  le text à mettre à la position définie
# pos: (int, int)               la position du centre du texte
# background: (int, int, int)   la couleur de fond du texte
# scale: (int, int)             le scale à appliquer sur le texte
# return: Rect                  le Rect qui correspond à la zone de texte
def showText(text, pos, background, scale):
    text_object = font.render(text, True, "black", background)
    if scale:
        text_object = pygame.transform.scale(text_object, scale)
    textRect = text_object.get_rect()
    textRect.center = pos
    screen.blit(text_object, textRect)
    return textRect
# Affiche une image (surface) à une certaine position
# image: Surface            la surface à mettre à la position définie
# pos: (int, int)           la position du centre de l'image
# scale: (int, int)         le scale à appliquer sur l'image
def showImage(image, pos, scale):
    scaled_image = pygame.transform.scale(image, scale)
    textRect = scaled_image.get_rect()
    textRect.center = pos
    screen.blit(scaled_image, textRect)
# La boucle de jeu
# Gère l'affichage du timer, et les clics de boutons
def mainloop():
    done = False
    while not done:
        for event in pygame.event.get():
            if event.type == TIMER_EVENT:
                game_controller.updateTimer()
            if event.type == AI_CLICK_EVENT:
                if not game_ai.stop and game_controller.timer_start:
                    game_ai.doOneMove()
            if event.type == pygame.QUIT:
                done = True
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if game_controller.end:
                    game_controller.onChooseDifficulty()
                else:
                    game_controller.onClick(event)
        clock.tick(30)
        pygame.display.update()

pygame.init()
# Couleurs
dark_grey = (100, 100, 100)
light_grey = (130, 130, 130)
red = (255, 0, 0)
# Setup de la partie
screen = pygame.display.set_mode((1000, 700))
screen.fill(dark_grey)
clock = pygame.time.Clock()
TIMER_EVENT = pygame.USEREVENT
AI_CLICK_EVENT = pygame.USEREVENT + 1
pygame.time.set_timer(TIMER_EVENT, 1000)
pygame.time.set_timer(AI_CLICK_EVENT, 40)
font = pygame.font.SysFont("Arial", 100)
pygame.display.set_caption('Démineur')
# Images
bomb_image = pygame.image.load("C:\\Users\\cedri\\python\\techno_emergente\\bombe.png").convert()
flag_image = pygame.image.load("C:\\Users\\cedri\\python\\techno_emergente\\drapeau.png").convert()
incorrect_flag_image = pygame.image.load("C:\\Users\\cedri\\python\\techno_emergente\\drapeauIncorrect.png").convert()
# Début de la partie
difficulties = [Difficulty("Facile", 15, 10, 10, 46, 500, 540), Difficulty("Moyen", 70, 25, 17, 36, 1000, 720), Difficulty("Difficile", 250, 50, 30, 21, 1250, 790)]
game_controller = GameController(0)
game_controller.showMainScreen()
game_ai = GameAi()
mainloop()
pygame.quit()
sys.exit()