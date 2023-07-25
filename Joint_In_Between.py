from PySide2 import QtCore
from PySide2 import QtGui
from PySide2 import QtWidgets
from shiboken2 import wrapInstance
import maya.cmds as cmds
import maya.OpenMaya as om
import maya.OpenMayaUI as omui


def maya_main_window():
    main_window_ptr = omui.MQtUtil.mainWindow()
    return wrapInstance(int(main_window_ptr), QtWidgets.QWidget)


class JointInBetween(QtWidgets.QDialog):
    joint_in_between_window = None

    @classmethod
    def show_dialog(cls):
        if not cls.joint_in_between_window:
            cls.joint_in_between_window = JointInBetween()

        if cls.joint_in_between_window.isHidden():
            cls.joint_in_between_window.show()
        else:
            cls.joint_in_between_window.raise_()
            cls.joint_in_between_window.activateWindow()

    def __init__(self, parent=maya_main_window()):
        super(JointInBetween, self).__init__(parent)

        self.setWindowTitle('Primitive Auto Rig')
        self.setMinimumSize(300, 80)

        self.setWindowFlag(QtCore.Qt.WindowContextHelpButtonHint, False)
        self.setWindowFlag(QtCore.Qt.WindowMinimizeButtonHint)
        # self.setWindowFlags(self.windowFlags() ^ QtCore.Qt.WindowContextHelpButtonHint)

        self.create_widgets()
        self.create_layout()
        self.create_connections()

        self.first_vertices = 1
        self.second_vertices = 1
        self.default_joint_number = 1
        self.joint_list = []

    def create_widgets(self):

        self.build_btn = QtWidgets.QPushButton("Build")
        self.first_edge_lineedit_lable = QtWidgets.QLabel("First Edge: ")
        self.first_edge_lineedit = QtWidgets.QLineEdit()
        self.first_edge_lineedit_button = QtWidgets.QPushButton("Select")
        self.second_edge_lineedit_lable = QtWidgets.QLabel("Second Edge: ")
        self.second_edge_lineedit = QtWidgets.QLineEdit()
        self.second_edge_lineedit_button = QtWidgets.QPushButton("Select")

        self.joint_number_lable = QtWidgets.QLabel("Joint Numbers: ")
        self.joint_number_lineedit = QtWidgets.QLineEdit()
        self.joint_number_lineedit.setText("1")

        self.visualize_chain_btn = QtWidgets.QPushButton("Visualize Chains")

        self.reverse_first_chain_btn = QtWidgets.QPushButton("Reverse 1st Chain")
        self.reverse_second_chain_btn = QtWidgets.QPushButton("Reverse 2nd Chain")

        self.create_curve_btn = QtWidgets.QPushButton("Create")
        self.close_btn = QtWidgets.QPushButton("Close")

    def create_layout(self):

        self.first_edge_layout = QtWidgets.QHBoxLayout()
        self.first_edge_layout.addWidget(self.first_edge_lineedit_lable)
        self.first_edge_layout.addWidget(self.first_edge_lineedit)
        self.first_edge_layout.addWidget(self.first_edge_lineedit_button)

        self.second_edge_layout = QtWidgets.QHBoxLayout()
        self.second_edge_layout.addWidget(self.second_edge_lineedit_lable)
        self.second_edge_layout.addWidget(self.second_edge_lineedit)
        self.second_edge_layout.addWidget(self.second_edge_lineedit_button)

        self.joint_number_layout = QtWidgets.QHBoxLayout()
        self.joint_number_layout.addWidget(self.joint_number_lable)
        self.joint_number_layout.addWidget(self.joint_number_lineedit)

        self.btn_layout = QtWidgets.QHBoxLayout()
        self.btn_layout.addWidget(self.create_curve_btn)
        self.btn_layout.addWidget(self.close_btn)

        self.reverse_layout = QtWidgets.QHBoxLayout()
        self.reverse_layout.addWidget(self.reverse_first_chain_btn)
        self.reverse_layout.addWidget(self.reverse_second_chain_btn)

        # add the Tab widget to the main layout
        self.main_layout = QtWidgets.QVBoxLayout(self)
        self.main_layout.addLayout(self.first_edge_layout)
        self.main_layout.addLayout(self.second_edge_layout)
        self.main_layout.addLayout(self.joint_number_layout)
        self.main_layout.addWidget(self.visualize_chain_btn)
        self.main_layout.addLayout(self.reverse_layout)
        self.main_layout.addLayout(self.btn_layout)
        # self.frame1.adjustSize()

    def create_connections(self):
        self.first_edge_lineedit_button.clicked.connect(self.select_first_edge)
        self.second_edge_lineedit_button.clicked.connect(self.select_second_edge)
        self.create_curve_btn.clicked.connect(self.create_curve)
        self.joint_number_lineedit.textChanged.connect(self.change_joint_number)

        self.visualize_chain_btn.clicked.connect(self.visualize)
        self.reverse_first_chain_btn.clicked.connect(self.reverse_first_chain)
        self.reverse_second_chain_btn.clicked.connect(self.reverse_second_chain)

        self.close_btn.clicked.connect(self.close)

    def select_first_edge(self):

        self.fisrt_sel_edge = cmds.ls(sl=True, fl=True)
        self.first_vertices = cmds.polyListComponentConversion(self.fisrt_sel_edge, fromEdge=True, toVertex=True)

        self.first_edge_lineedit.setText(str(self.first_vertices))

    def select_second_edge(self):
        self.second_sel_edge = cmds.ls(sl=True, fl=True)
        self.second_vertices = cmds.polyListComponentConversion(self.second_sel_edge, fromEdge=True, toVertex=True)
        self.second_edge_lineedit.setText(str(self.second_vertices))

        if len(self.first_vertices) > len(self.second_vertices):
            self.default_joint_number = len(self.first_vertices)
            self.joint_number_lineedit.setText(str(int(self.default_joint_number) + 1))

        if len(self.first_vertices) < len(self.second_vertices):
            self.default_joint_number = len(self.second_vertices)
            self.joint_number_lineedit.setText(str(int(self.default_joint_number) + 1))

    def change_joint_number(self):
        self.default_joint_number = int(self.joint_number_lineedit.text()) - 1

    def visualize(self):
        self.first_curve_pos = []
        self.second_curve_pos = []
        self.average_pos = []
        self.first_crv_chain = []
        self.second_crv_chain = []

        cmds.polyToCurve(self.fisrt_sel_edge, n="first_crv_temp", form=2, degree=1, ch=False)[0]
        first_curve = cmds.ls("first_crv_temp")

        cmds.polyToCurve(self.second_sel_edge, n="second_crv_temp", form=2, degree=1, ch=False)[0]
        second_curve = cmds.ls("second_crv_temp")

        if len(self.first_vertices) > len(self.second_vertices):
            second_curve = cmds.rebuildCurve(second_curve, d=1, s=len(self.first_vertices), rpo=True, ch=False)
        if len(self.first_vertices) < len(self.second_vertices):
            first_curve = cmds.rebuildCurve(first_curve, d=1, s=len(self.second_vertices), rpo=True, ch=False)

        first_curve = cmds.rebuildCurve(first_curve, d=1, s=int(self.default_joint_number), rpo=True, ch=False)
        second_curve = cmds.rebuildCurve(second_curve, d=1, s=int(self.default_joint_number), rpo=True, ch=False)

        first_curve_cvs = cmds.ls("{}.cv[:]".format(first_curve[0]), fl=True)
        second_curve_cvs = cmds.ls("{}.cv[:]".format(second_curve[0]), fl=True)

        for cv in first_curve_cvs:
            cv_pos = cmds.xform(cv, q=True, ws=True, t=True)
            self.first_curve_pos.append(cv_pos)
            first_crv_chain_jnt = cmds.joint(n="first_chain_jnt#", p=(cv_pos[0], cv_pos[1], cv_pos[2]))
            self.first_crv_chain.append(first_crv_chain_jnt)
        cmds.select(cl=True)

        for cv in second_curve_cvs:
            cv_pos = cmds.xform(cv, q=True, ws=True, t=True)
            self.second_curve_pos.append(cv_pos)
            second_crv_chain_jnt = cmds.joint(n="second_chain_jnt#", p=(cv_pos[0], cv_pos[1], cv_pos[2]))
            self.second_crv_chain.append(second_crv_chain_jnt)
        cmds.select(cl=True)
        cmds.delete(first_curve)
        cmds.delete(second_curve)

    def reverse_first_chain(self):
        print(self.first_crv_chain)
        cmds.select(self.first_crv_chain[-1])
        cmds.RerootSkeleton()
        self.first_crv_chain.reverse()
        self.first_curve_pos.reverse()
        print(self.first_crv_chain)

    def reverse_second_chain(self):
        cmds.select(self.second_crv_chain[-1])
        cmds.RerootSkeleton()
        self.second_crv_chain.reverse()
        self.second_curve_pos.reverse()

    def create_curve(self):
        cmds.select(cl=True)
        for avg in zip(self.first_curve_pos, self.second_curve_pos):
            print(avg)
            avg_x = float(avg[0][0] + avg[1][0]) / 2
            avg_y = float(avg[0][1] + avg[1][1]) / 2
            avg_z = float(avg[0][2] + avg[1][2]) / 2
            avg_pos = (avg_x, avg_y, avg_z)
            self.average_pos.append(avg_pos)


        for point in self.average_pos:
            jnt = cmds.joint(n="in_between_jnt#", p=point)
            self.joint_list.append(jnt)

        cmds.joint(self.joint_list[0], e=True, oj="yxz", secondaryAxisOrient="zup", ch=True)

        cmds.delete(self.first_crv_chain)
        cmds.delete(self.second_crv_chain)


if __name__ == '__main__':
    try:
        joint_in_between_window.close()
        joint_in_between_window.deleteLater()
    except:
        pass

    joint_in_between_window = JointInBetween()
    joint_in_between_window.show()
