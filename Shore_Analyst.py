# -*- coding: utf-8 -*-
"""
/***************************************************************************
 ShorelineAnalyst
                                 A QGIS plugin
 Plugin to Analise the shorelines of a Coast line
                              -------------------
        begin                : 2016-03-22
        git sha              : $Format:%H$
        copyright            : (C) 2016 by Manuel Sa
        email                : manuelsa@ua.pt
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""
from PyQt4.QtCore import *#QSettings, QTranslator, qVersion, QCoreApplication
from PyQt4.QtGui import *#QAction, QIcon, QFileDialog
from PyQt4 import *
from glob import *
from qgis.gui import *
from qgis.core import *
from qgis.utils import*

# Initialize Qt resources from file resources_rc.py
import resources_rc
# Import the code for the dialog
from Shore_Analyst_dialog import ShorelineAnalystDialog
import os.path
import processing
from processing.tools import *




class ShorelineAnalyst:
    """QGIS Plugin Implementation."""

    def __init__(self, iface):
        """Constructor.

        :param iface: An interface instance that will be passed to this class
            which provides the hook by which you can manipulate the QGIS
            application at run time.
        :type iface: QgsInterface
        """
        # Save reference to the QGIS interface
        self.iface = iface
        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)
        # initialize locale
        locale = QSettings().value('locale/userLocale')[0:2]
        locale_path = os.path.join(
            self.plugin_dir,
            'i18n',
            'ShorelineAnalyst_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)

            if qVersion() > '4.3.3':
                QCoreApplication.installTranslator(self.translator)

        # Create the dialog (after translation) and keep reference
        self.dlg = ShorelineAnalystDialog()

        # Declare instance attributes
        self.actions = []
        self.menu = self.tr(u'&Shoreline Analyst')
        # TODO: We are going to let the user set this up in a future iteration
        self.toolbar = self.iface.addToolBar(u'ShorelineAnalyst')
        self.toolbar.setObjectName(u'ShorelineAnalyst')
        

    # noinspection PyMethodMayBeStatic
    def tr(self, message):
        """Get the translation for a string using Qt translation API.

        We implement this ourselves since we do not inherit QObject.

        :param message: String for translation.
        :type message: str, QString

        :returns: Translated version of message.
        :rtype: QString
        """
        # noinspection PyTypeChecker,PyArgumentList,PyCallByClass
        return QCoreApplication.translate('ShorelineAnalyst', message)


    def add_action(
        self,
        icon_path,
        text,
        callback,
        enabled_flag=True,
        add_to_menu=True,
        add_to_toolbar=True,
        status_tip=None,
        whats_this=None,
        parent=None):
        """Add a toolbar icon to the toolbar.

        :param icon_path: Path to the icon for this action. Can be a resource
            path (e.g. ':/plugins/foo/bar.png') or a normal file system path.
        :type icon_path: str

        :param text: Text that should be shown in menu items for this action.
        :type text: str

        :param callback: Function to be called when the action is triggered.
        :type callback: function

        :param enabled_flag: A flag indicating if the action should be enabled
            by default. Defaults to True.
        :type enabled_flag: bool

        :param add_to_menu: Flag indicating whether the action should also
            be added to the menu. Defaults to True.
        :type add_to_menu: bool

        :param add_to_toolbar: Flag indicating whether the action should also
            be added to the toolbar. Defaults to True.
        :type add_to_toolbar: bool

        :param status_tip: Optional text to show in a popup when mouse pointer
            hovers over the action.
        :type status_tip: str

        :param parent: Parent widget for the new action. Defaults None.
        :type parent: QWidget

        :param whats_this: Optional text to show in the status bar when the
            mouse pointer hovers over the action.

        :returns: The action that was created. Note that the action is also
            added to self.actions list.
        :rtype: QAction
        """

        icon = QIcon(icon_path)
        action = QAction(icon, text, parent)
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)

        if status_tip is not None:
            action.setStatusTip(status_tip)

        if whats_this is not None:
            action.setWhatsThis(whats_this)

        if add_to_toolbar:
            self.toolbar.addAction(action)

            
        if add_to_menu:
            self.iface.addPluginToMenu(
                self.menu,
                action)

        self.actions.append(action)

        return action

    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""

        icon_path = ':/plugins/ShorelineAnalyst/icon.png'
        self.add_action(
            icon_path,
            text=self.tr(u'Shoreline Analyst'),
            callback=self.run,
            parent=self.iface.mainWindow())


    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        for action in self.actions:
            self.iface.removePluginMenu(
                self.tr(u'&Shoreline Analyst'),
                action)
            self.iface.removeToolBarIcon(action)
        # remove the toolbar
        del self.toolbar

    def select_output_file(self):
        filename = QFileDialog.getSaveFileName(self.dlg, "Select output file","",'*.shp') #cria Ficheiro output
        self.dlg.lineEdit.setText(filename)
    
        
    def run(self):
        
        
        
        # Limpar ficheiros da Pasta temp 
        current_directory = os.path.dirname(os.path.abspath(__file__))
        current_directory_1 = current_directory + "\\temp\\"
        
        #files = glob.glob(current_directory_1 + "\\*.shp")
        #for file in files:
        #    os.unlink(file)
        
        #files = glob.glob(current_directory_1 + "\\*.dbf")
        #for file in files:
        #    os.unlink(file)
        
        
        layers = self.iface.legendInterface().layers() # Chamar baseline
        layer_list = []
        # Limpar os Vectores de trabalho anteriores do mapLayer
        for layer in QgsMapLayerRegistry.instance().mapLayers().values():
            if layer.name() in ["outputold","outputnew", "outputnnn", "disthub1","disthub2","baseline","UA_1","UA_2", "UAOUT", "Result"]:
                QgsMapLayerRegistry.instance().removeMapLayers( [layer.id()] )
               
            layer_list.append(layer.name())
        
        #Prencher a combobox da baseline
        #self.dlg.baseline.clear()
        #self.dlg.baseline.addItems(layer_list)
        
        #Prencher a combobox da shoreline 1
        self.dlg.shoreline1.clear()
        self.dlg.shoreline1.addItems(layer_list) 
        
        #Prencher a combobox da shoreline 2
        self.dlg.shoreline2.clear()
        self.dlg.shoreline2.addItems(layer_list)
        
        
        list1 = ['10','100','1000','2000']
        
        
        #Prencher a combobox com valores de precisao
        self.dlg.number1.clear()
        self.dlg.number1.addItems(list1)
        
       
        # show the dialog
        self.dlg.show()
        # Run the dialog event loop
        result = self.dlg.exec_()
        # See if OK was pressed
        if result:
            
            
            shorelineold = self.dlg.shoreline1.currentIndex()
            selectedLayer1 = layers[shorelineold]
            
            
            shorelinenew = self.dlg.shoreline2.currentIndex()
            selectedLayer2 = layers[shorelinenew]
            
            numbers = self.dlg.number1.currentIndex()
            selected_str = list1[numbers]
            selected = float(selected_str)
            baseline_points = selected * 10
            
            outputold = current_directory_1 + 'outputold.shp'
            outputnew = current_directory_1 + 'outputnew.shp'
            outputnnn = current_directory_1 + 'outputnnn.shp'
            outputlol = current_directory_1 + 'outputlol.shp'
            disthub1 = current_directory_1 + 'disthub1.shp'
            disthub2 = current_directory_1 + 'disthub2.shp'
            disthubold = current_directory_1 + 'disthubold.shp'
            disthubnew = current_directory_1 + 'disthubnew.shp'
            UA_1 = current_directory_1 + 'UA_1.shp'
            UA_1table = current_directory_1 + 'UA_1.dbf'
            UA_2 = current_directory_1 + 'UA_2.shp'
            UA_2table = current_directory_1 + 'UA_2.dbf'
            UAA = current_directory_1 + 'UAA.shp'
            UAOUT = current_directory_1 + 'UAOUT.shp'
            FinalResult = current_directory_1 + 'FinalResult.shp'
            shorelinefinal2 = current_directory_1 + 'shorelinefinal2.shp'
            estilo = current_directory + 'estilo.qml'
            FinalResult2 = current_directory_1 + 'FinalResult2.shp'
            
            
            BASELINECREATE = processing.runalg('gdalogr:singlesidedbuffersandoffsetlinesforlines', selectedLayer1, 1, 'geometry', '1000', 0, False, None, False, None, outputnnn) #novo baseline
            FIELDTABLE1 = processing.runalg('qgis:addfieldtoattributestable', selectedLayer1,'hub1',1,10.0,0.0, outputold)
            FIELDTABLE2 = processing.runalg('qgis:addfieldtoattributestable', selectedLayer2,'hub2',1,10.0,0.0, outputnew)
            
            # Processing script
            CONVERT1 = processing.runalg('saga:convertlinestopoints', outputold, True, selected, outputold)
            CONVERT2 = processing.runalg('saga:convertlinestopoints', outputnew, True, selected, outputnew)
            CONVERT3 = processing.runalg('saga:convertlinestopoints', outputnnn, True, baseline_points, outputlol)
            
            #Calcula as distancias entre a baseline as linhas de costa
            DISTHUB1 = processing.runalg('qgis:distancetonearesthub',outputlol,outputold,'hub1',1,0, disthub1)
            DISTHUB2 = processing.runalg('qgis:distancetonearesthub',outputlol,outputnew,'hub2',1,0, disthub2)
            
            # Calcular valores Disthub1 e Dishub2, alterando primeiro o nome da coluna respectivamente. 
            FIELDCALCULATOR1 =processing.runalg('qgis:fieldcalculator', disthub1,'Disthubold',0,10.0,3.0,True,'HubDist', disthubold)
            FIELDCALCULATOR2 =processing.runalg('qgis:fieldcalculator', disthub2,'Disthubnew',0,10.0,3.0,True,'HubDist', disthubnew)
            
            #
            FIELDCALCULATOR_1=processing.runalg('qgis:fieldcalculator', disthubold,'UA_1',1,10.0,3.0,True,'$rownum',UA_1)
            
            FIELDCALCULATOR_2=processing.runalg('qgis:fieldcalculator', disthubnew,'UA_2',1,10.0,3.0,True,'$rownum',UA_2)
            
            # juntar
            JOINATTRIBUTESTABLE_1=processing.runalg('qgis:joinattributestable', UA_1, UA_2table, 'UA_1', 'UA_2', UAOUT)
            
            
            FIELDCALCULATOR3 = processing.runalg('qgis:fieldcalculator', UAOUT,'Result',0,10.0,3.0,True, '"Disthubnew" - "Disthubold"', FinalResult)
            
            FIELDCALCULATOR4 = processing.runalg('qgis:fieldcalculator', FinalResult,'Perc',0,10.0,3.0,True, '(("Disthubnew" - "Disthubold")/"Disthubold")*100', FinalResult2)
            
            
            FIELDCALCULATOR_5=processing.runalg('qgis:fieldcalculator', selectedLayer1,'UA_3',1,10.0,3.0,True,'$rownum',UAA)
            #JOINATRTRIBUTELOC=processing.runalg('qgis:joinattributesbylocation', UAA, FinalResult2, 0, sum, min, max, 0, 1, shorelinefinal2)
            
            
            
            
            
            #Resultado final
            JOINATTRIBUTESTABLE_1=processing.runalg('qgis:joinattributestable', FinalResult2, UAA, 'UA_3', 'UA_1', shorelinefinal2)
            CONVERT1 = processing.runalg('saga:convertlinestopoints', shorelinefinal2, True, selected, shorelinefinal2)
            
            #FIELDCALCULATOR4 = processing.runalg('qgis:fieldcalculator', shoreline_final,'Result',0,10.0,3.0,True, '"Disthubnew" - "Disthubold"', FinalResult)
            # alterei o shoreline final pelo FinalResult.
            SET_STYLE=processing.runalg('qgis:setstyleforvectorlayer', shorelinefinal2, estilo)
            
 
            #layer = self.iface.addVectorLayer(shorelinefinal2, "shorelinefinal2, "ogr")
            #if not layer:
            #    print "Layer failed to load!"
            
            
                
            pass    
        pass
    pass