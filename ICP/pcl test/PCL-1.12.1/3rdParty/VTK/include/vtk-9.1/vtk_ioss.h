/*=========================================================================

  Program:   Visualization Toolkit
  Module:    vtk_exodusII.h

  Copyright (c) Ken Martin, Will Schroeder, Bill Lorensen
  All rights reserved.
  See Copyright.txt or http://www.kitware.com/Copyright.htm for details.

     This software is distributed WITHOUT ANY WARRANTY; without even
     the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR
     PURPOSE.  See the above copyright notice for more information.

=========================================================================*/
#ifndef vtk_ioss_h
#define vtk_ioss_h

/* Use the ioss library configured for VTK.  */
#define VTK_MODULE_USE_EXTERNAL_vtkioss 0

#if VTK_MODULE_USE_EXTERNAL_vtkioss
# define VTK_IOSS(x) <x>
#else
# define VTK_IOSS(x) <vtkioss/x>
#endif

#endif
