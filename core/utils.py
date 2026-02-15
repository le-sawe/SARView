# -*- coding: utf-8 -*-
import time
from qgis.core import (
    QgsProject,
    QgsRasterLayer,
    QgsRasterBandStats,
    QgsContrastEnhancement,
    QgsSingleBandGrayRenderer
)
from qgis.analysis import QgsRasterCalculator, QgsRasterCalculatorEntry

def apply_log_scale(input_layer, factor):

    instance = QgsRasterCalculatorEntry()
    instance.ref = 'raster@1' 
    instance.raster = input_layer
    instance.bandNumber = 1
    entries = [instance]
    
    gdal_formula = f"{factor} * log10(raster@1 + 0.00001)"
    
    timestamp = int(time.time())
    output_path = f"/vsimem/sar_log_{timestamp}.tif"
    
    calc = QgsRasterCalculator(
        gdal_formula, 
        output_path, 
        "GTiff", 
        input_layer.extent(), 
        input_layer.width(), 
        input_layer.height(), 
        entries,
        QgsProject.instance().transformContext() 
    )
    
    result = calc.processCalculation()
    
    if result == 0:
        log_layer = QgsRasterLayer(output_path, f"{input_layer.name()} (dB)")
        if log_layer.isValid():
            QgsProject.instance().addMapLayer(log_layer)
            return log_layer
    else:
        print(f"Calculation Error Code: {result}")
        
    return None

def apply_outlier_stretch(layer, std_dev_mult):

    provider = layer.dataProvider()
    band = 1
    stats = provider.bandStatistics(band, QgsRasterBandStats.All)
    
    low_cut = stats.mean - (std_dev_mult * stats.stdDev)
    high_cut = stats.mean + (std_dev_mult * stats.stdDev)
    
    low_cut = max(stats.minimumValue, low_cut)
    high_cut = min(stats.maximumValue, high_cut)
    
    enhancement = QgsContrastEnhancement(provider.dataType(band))
    enhancement.setContrastEnhancementAlgorithm(QgsContrastEnhancement.StretchToMinimumMaximum)
    enhancement.setMinimumValue(low_cut)
    enhancement.setMaximumValue(high_cut)

    renderer = QgsSingleBandGrayRenderer(provider, band)
    renderer.setContrastEnhancement(enhancement)
    
    layer.setRenderer(renderer)
    layer.triggerRepaint()