import pygame, string
import threading
import sys

background_image = pygame.image.load('A.png')
background_image = pygame.transform.scale(background_image, (800, 600))


class RenderEngine:
    def __init__(self):
        self.screen = pygame.display.set_mode((800, 600))
        pygame.display.set_caption("Необычная головоломка")
        self.background_rect = background_image.get_rect()
        self.render_queue_list = []
        pygame.font.init()
        self.font = pygame.font.Font(None, 36)

    def render_frame(self, text):
        # Следущий код немного "костылявый"? Ибо жалко было удалять то что больше не нужно, или нужно...
        self.screen.blit(background_image, self.background_rect)
        i = 0
        k = 0

        for text_element in text:
            if text_element == "entails":
                i -= 20
                string = ""
                Max = 0
                for text_element2 in text:
                    if text_element2 != text_element:
                        length = len(text_element2.replace(" ", "").replace("->", "→"))
                        if length > Max:
                            Max = length

                for _ in range(Max):
                    string = string + "—"
                new_text = self.font.render(string, True, (255, 255, 255))
                self.screen.blit(new_text, (10, 10 + i))
                i -= 20
            else:

                new_text = self.font.render(text_element, True, (255, 255, 255))
                self.screen.blit(new_text, (10, 10 + i))
            i += 40
            k += 1

        pygame.display.update()
# А дальше вроде более менее нормальный код

logicalOperators = ["->", "/\\", "\\/", '~']
logicalConstants = ['_|_']

def isPropositionMeaningless(prop):
    deepness = 0
    for symbol in prop:
        if symbol == "(" and deepness >= 0:
            deepness += 1
        elif symbol == ")" and deepness >= 0:
            deepness -= 1
    return deepness != 0

def deleteUnnecessarily(prop):
    if prop[0] == '(':
        newprop = prop[1:(len(prop) - 1)]
        if not isPropositionMeaningless(newprop):
            return newprop
    return prop
    
def createPIfNecessary(prop):
    if len(prop) > 1 and prop != "_|_":
        return '(' + prop + ')'
    else:
        return prop

def Deeper(prop, includeOperator):
    success = 0
    deepness = 0
    stopcountingdd = False
    defaultdeepness = 0
    successDictionary = {}
    for i in range(len(prop)):
        symbol = prop[i]
        if symbol == '(':
            deepness += 1
            if not stopcountingdd:
                defaultdeepness += 1
        elif symbol == ')':
            deepness -= 1
        if symbol != '(':
            stopcountingdd = True
        for operator in logicalOperators:
            if not operator in successDictionary:
                successDictionary[operator] = 0
            if symbol == operator[successDictionary[operator]] and deepness == 0:
                successDictionary[operator] += 1
                if successDictionary[operator] == len(operator):
                    if operator != '~':
                        Array = [prop[0:(i - successDictionary[operator])], prop[(i + 2):len(prop)]]
                        if includeOperator:
                            Array.append(operator)
                        return Array
                    else:
                        Array = [prop[0:i], prop[(i+1):len(prop)]]
                        if Array[0] == "":
                            Array.pop(0)
                        if includeOperator:
                            Array.append(operator)
                        return Array
            else:
                successDictionary[operator] = 0

def GetDeepestLevel(prop, level=0):
    if prop == None:
        return level
    deeperStructure = Deeper(prop, False)
    if not deeperStructure:
        return level
    Max = level
    for deeperProp in deeperStructure:
        GDL = GetDeepestLevel(deleteUnnecessarily(deeperProp), level)
        if GDL > Max:
            Max = GDL
    return Max + 1

def GetDeepestLevelOfPropositions(propArray, level=0):
    Max = level
    for prop in propArray:
        GDL = GetDeepestLevel(deleteUnnecessarily(prop), level)
        if GDL > Max:
            Max = GDL
    return Max

def ConstructStructureOfPropositionStructure(propArray, level=9999):
    if level == 0:
        return propArray
    newPropArray = []
    for prop in propArray:
        deeper = Deeper(deleteUnnecessarily(prop), True)
        if prop in logicalOperators or deeper == None:
            newPropArray.append(prop)
            continue
        newPropArray.append(ConstructStructureOfPropositionStructure(deeper, level - 1))
    return newPropArray

def ConstructStructureOfPropositions(Array, level=9999):
    structures = []
    for prop in Array:
        structures.append(ConstructStructureOfPropositionStructure([prop], level))
    return structures

def ConstructSymmetricDeepUnionStructure(infPropArray, propArray):
    newPropArray = []
    for i in range(len(infPropArray)):
        newPropArray.append(ConstructStructureOfPropositions([propArray[i]], GetDeepestLevelOfPropositions([infPropArray[i]])))
    return deepPropUnion(newPropArray)

def lengthyDeepPropUnion(newPropArray, propStructure):
    for propSubstructure in propStructure:
        if isinstance(propSubstructure, str):
            newPropArray.append(propSubstructure)
        else:
            lengthyDeepPropUnion(newPropArray, propSubstructure)
    return newPropArray

def deepPropUnion(propStructure):
    newPropArray = []
    lengthyDeepPropUnion(newPropArray, propStructure)
    return newPropArray

def isStructureTheSamePlusVariableAssingment(infArray, linesArray):
    infStructure = deepPropUnion(ConstructStructureOfPropositionStructure(infArray))
    linesStructure = ConstructSymmetricDeepUnionStructure(infArray, linesArray)
    infLen = len(infStructure)
    if infLen != len(linesStructure):
        return [False, []]
    Check = True
    VariableAssingment = {}
    for i in range(len(linesStructure)):
        linesStructure[i] = deleteUnnecessarily(linesStructure[i])
    for i in range(infLen):
        if infStructure[i] in infStructure[0:i]:
            if not linesStructure[i] in linesStructure[0:i]:
                Check = False
                break
            if infStructure[0:i].index(infStructure[i]) != linesStructure[0:i].index(linesStructure[i]):
                Check = False
                break
        if infStructure[i] in logicalOperators and linesStructure[i] != infStructure[i]:
            Check = False
            break
        if infStructure[i] in logicalConstants and linesStructure[i] != infStructure[i]:
            Check = False
            break
        if not infStructure[i] in logicalOperators and not infStructure[i] in logicalConstants:
            VariableAssingment[infStructure[i]] = linesStructure[i]
    return [Check, VariableAssingment]

re = RenderEngine()
i = 3
k = 1

'''re.render_frame([
                    "Здесь правила. Под символы правил можно подставить формулу. Например, для mp можно под p поставить p -> q, а под q - q -> r, отсюда правило: ",
                    "выведенное правило:", "(p -> q) -> (q -> r)", "p -> q", "q -> r", "", "mp:", "p -> q", "p",
                    "entails", "q"])
pygame.time.wait(1000)'''

InferenceRules = {
    "mp": ["p -> q", "p", "q"],
#    "di": ["p", "p \/ q"],
    "de": ["p -> r", "q -> r", "p \/ q", "r"],
    "ce1": ["p /\ q", "p"],
    "ce2": ["p /\ q", "q"],
    "ci": ["p", "q", "p /\ q"],
    "ds1": ["p \/ q", "~p", "q"],
    "ds2": ["p \/ q", "~q", "p"],
    "fi": ["p", "~p", "_|_"],
    "ni": ["p -> _|_", "~p"]
}

InferenceRules["ie"] = InferenceRules["mp"]
InferenceRules["->e"] = InferenceRules["ie"]
InferenceRules["\/e"] = InferenceRules["de"]
InferenceRules["/\e1"] = InferenceRules["ce1"]
InferenceRules["/\e2"] = InferenceRules["ce2"]
#InferenceRules["\/i"] = InferenceRules["di"]
InferenceRules["/\i"] = InferenceRules["ci"]
InferenceRules["_|_i"] = InferenceRules["fi"]
InferenceRules["~i"] = InferenceRules["ni"]
InferenceRules["raa"] = InferenceRules["ni"]
InferenceRules["aaa"] = InferenceRules["raa"]
InferenceRules["contradict"] = InferenceRules["fi"]
InferenceRules["contradiction"] = InferenceRules["fi"]

def mainReadThread(puzzles):
    global indexedProp
    global goal
    for puzzle in puzzles:
        prop = puzzle[0]
        goal = puzzle[1]
        extraAssumptions = {}
        while (not goal in prop) or extraAssumptions:
            indexedProp = []
            for i in range(len(prop)):
                newProp = str(i + 1) + ". " + prop[i]
                if i in extraAssumptions.values():
                    newProp = newProp + (" " * (60 - len(newProp) * 2)) + "Предположение."
                indexedProp.append(newProp)
            Inference = input("Напишите сюда правило вывода и строки для них.")
            Split = Inference.split(" ")
            InputIRule = Split[0]
            Split.remove(InputIRule)
            Lines = Split

            if InputIRule in InferenceRules:
                PremisesPlusConclusion = InferenceRules[InputIRule]
                Premises = PremisesPlusConclusion[0:(len(PremisesPlusConclusion) - 1)]
                proposedPremises = []
                for premiseIndex in Split:
                    proposedPremises.append(prop[int(premiseIndex) - 1])
                structureSubstitution = isStructureTheSamePlusVariableAssingment(PremisesPlusConclusion[0:(len(PremisesPlusConclusion) - 1)], proposedPremises)
                if not structureSubstitution[0]:
                    print("Структура предложенных строк не совпадает со структурой правила.")
                    continue
                for propVariable in structureSubstitution[1]:
                    structureSubstitution[1][propVariable] = createPIfNecessary(structureSubstitution[1][propVariable])
                substitutedExpression = PremisesPlusConclusion[len(PremisesPlusConclusion) - 1].translate(str.maketrans(structureSubstitution[1]))
                substitutedExpression = deleteUnnecessarily(substitutedExpression)
                prop.append(substitutedExpression)
            else:
                if InputIRule != "assume" and InputIRule != "->i" and InputIRule != "ii" and InputIRule != "cp" and InputIRule[0:2] not in ["di", "\/i"]:
                    print("Не распознано правило вывода.")
                elif InputIRule == "assume":
                    newProp = Inference.replace("assume ", "")
                    if newProp in extraAssumptions:
                        print("Утверждение уже предположено.")
                        continue
                    extraAssumptions[newProp] = len(prop)
                    prop.append(newProp)
                elif InputIRule[0:2] in ["di", "\/i"]:
                    if len(Lines) < 2:
                        print(f"Недостаточно аргументов. Ожидаемое кол-во аргументов: 2 или больше, получено: {len(Lines)}")
                        continue
                    if (len(InputIRule) < 3):
                        print("Не указан номер версии правила вывода. Напишите, например, di1 или di2.")
                        continue
                    p = createPIfNecessary(prop[int(Lines[0]) - 1])
                    Lines.pop(0)
                    q = Lines[0]
                    for line in Lines[1:len(Lines)]:
                        q = q + " " + line
                    q = createPIfNecessary(q)
                    if InputIRule[2] == '1':
                        prop.append(p +  " \/ " + q)
                    elif InputIRule[2] == '2':
                        prop.append(q +  " \/ " + p)
                    else:
                        print("Напишите число после di или \/i. Например, di1 или di2.")
                        continue
                elif extraAssumptions:
                    if Lines[0] == '':
                        print("Отсутствует число.")
                        continue
                    Max = [0, ""]
                    for prop1 in extraAssumptions:
                        if extraAssumptions[prop1] >= Max[0]:
                            Max[0] = extraAssumptions[prop1]
                            Max[1] = prop1
                    if int(Lines[0]) > len(prop):
                        print("Указан слишком большой индекс.")
                        continue
                    newProp = prop[int(Lines[0]) - 1]
                    del extraAssumptions[Max[1]]
                    for i in range(len(prop) - Max[0]):
                        prop.pop()
                    Max[1] = createPIfNecessary(Max[1])
                    newProp = createPIfNecessary(newProp)
                    prop.append(Max[1] + " -> " + newProp)
                else:
                    print("Нет дополнительных предположений.")
        indexedProp = []
        for i in range(len(prop)):
            indexedProp.append(str(i + 1) + ". " + prop[i])
        pygame.time.wait(1000)
        indexedProp.append("Ч. Т. Д.")
        pygame.time.wait(1000)
        indexedProp = ["Цель достигнута!"]
        pygame.time.wait(2000)
    indexedProp = ["Поздравляем! вы прошли игру!", "Технически головоломки можно создавать и создавать, и даже предлагать", "собственные теоремы для доказатеьства, но я этого пока не сделал."]


goal = "r"
prop = ["p -> (q -> r)", "p -> q", "p"]

indexedProp = []
th = threading.Thread(target=mainReadThread, args=([[
    [["p -> q", "p"], "p /\ q"],
    [["p -> (q -> r)", "p -> q", "p"], "r"],
    [["(p -> (q -> r)) /\ (p -> q)", "p"], "r"],
    [[], "p -> (q -> p)"],
    [[], "p -> (~(~p))"],
    [[], "~(~(p \/ (~p)))"],
    [["p /\ ~p"], "q"],
    [[], "(p -> q) -> ((~q) -> (~p))"],
    [[], "(p -> q) -> ((q -> r) -> (p -> r))"],
    [[], "p -> ((~(~p)) /\ (p \/ (~p)))"],
    [[], "((p /\ q) -> (q /\ p)) /\ ((p \/ q) -> (q \/ p))"],
    [[], "_|_ -> p"]
]]))
th.start()

while True:
    events = pygame.event.get()
    for event in events:
        if event.type == pygame.QUIT:
            sys.exit()
    re.render_frame([("Цель: " + goal)] + indexedProp)
    pygame.time.wait(10)

pygame.time.wait(11111111)