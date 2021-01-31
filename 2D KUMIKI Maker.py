"""SOTSUSEI"""

import rhinoscriptsyntax as rs
import sys

"""
# PARAMETERs
    # TSUGITE
        x_m     int     x length of material
        y_m     int     y length of material
        z_m     int     z length of material

        x_k     int     x length of KUMIKI

        # LIST
        KUMIKI_info    [m_info, m_model]

            m_info          [x_m, y_m, z_m, m_points, layer_t]
            m_points        [l_mp0, l_mp1, r_mp0, r_mp1]

    # SHIGUCHI
        x_m1    int     x length of material1
        y_m1    int     y length of material1

        x_m2    int     x length of material2
        y_m2    int     y length of material2

        z_m     int     z length of material (thickness)

        x_k     int     x length of KUMIKI
        y_k     int     y length of KUMIKI

        # LIST
        KUMIKI_info     [m1_info, m2_info, m1_model, m2_model]

            m1_info         [x_m1, y_m1, z_m, m1_points]
            m1_points       [m1_p0, m1_p1, m1_p2, m1_p3]

            m2_info         [x_m2, y_m2, z_m, m2_points]
            m2_points       [m2_p0, m2_p1, m2_p2, m2_p3]

    # SEN
        w_sen       int     width of SEN
        n_w_sen     int     width of narrow part of SEN
        h_sen       int     height of SEN
        t_sen       int     thickness of SEN

        n           int     the number of SEN
        set         int     set back length from edge line of material
        offset      num     the number of offset between each SENs

"""

# FUNCTIONs---------------------------------------------------------------------
def delete_all():
    """Delete all objects if user wants."""
    strings = ['Yes', 'No']
    str = rs.GetString("Do you want to erase all objects?", 'Yes', strings)

    if str == 'Yes':
        obs = rs.ObjectsByType(0)
        rs.DeleteObjects(obs)
    else:
        pass

# CONTROLL FUNCTION-------------------------------------------------------------
def RUN():
    """Runner of this code. Most Top LEVEL function.
    Receives:
        ---
    Returns:
        ---
    """
    """
    # NOTE:
    The flow of this code.
    1   type of KUMIKI -> TSUGITE or SHIGUCHI
    2   decide which KUMIKI to make -> ex. TSUGITE -> ARI, SHIGUCHI -> TOME
    3   get information to make KUMIKI which decided
    4   make 3D KUMIKI (exisiting KUMIKI Shape) and show model to user
    5   if the 3D KUMIKI is OK, make 2D KUMIKI ver.( & Processing Data)
    6   make 3D model of 2D KUMIKI which includes the SEN shape.
    """

    KUMIKI_type = ask_KUMIKI_type()
    KUMIKI_name = decide_KUMIKI(KUMIKI_type)
    KUMIKI_info = get_information(KUMIKI_type)

    crvs1, crvs2, SEN_info = make_KUMIKI(KUMIKI_type, KUMIKI_name, KUMIKI_info)


    make_SEN_crvs(KUMIKI_type, KUMIKI_info, SEN_info)

    deploy_crvs(KUMIKI_type, KUMIKI_info, crvs1, crvs2)

    rs.ZoomExtents()

# FUNCTIONs---------------------------------------------------------------------
def ask_KUMIKI_type():
    """Asks KUMIKI type ; TSUGITE or SHIGUCHI
    Receives:
        ---
    Returns:
        KUMIKI_type     str     Type of KUMIKI ; TSUGITE or SHIGUCHI
    """

    # message
    message1 = "Choose type of KUMIKI to make.\
                            'KUMIKI' : Traditional Wood Joint System."
    rs.MessageBox(message1, 0, 'KUMIKI Type')

    """
    message2 = "'TSUGITE' : A technique to connect materials to augment the lack of length of\
    available materials.    'SHIGUCHI' A technique to connect materials at an angle."
    rs.MessageBox(message2, 0, 'KUMIKI Type')
    """

    # get strings
    strings = ['TSUGITE', 'SHIGUCHI']
    KUMIKI_type = rs.GetString("Which type of KUMIKI to make?", None, strings)

    print (KUMIKI_type)

    return KUMIKI_type

def decide_KUMIKI(KUMIKI_type):
    """Decides KUMIKI to make.
    Receives:
        KUMIKI_type     str     Type of KUMIKI ; TSUGITE or SHIGUCHI
    Returns:
        KUMIKI_name     str     Name of KUMIKI
    """
    # message
    message0 = "Choose type of KUMIKI to make."
    rs.MessageBox(message0, 0, "KUMIKI Type")

    # get strings
    if KUMIKI_type == 'TSUGITE':
        # message
        TSUGITE_strings = ['ARI', 'KAMA', 'RYAKUKAMA', 'MECHIGAI', 'AIKAKI',\
        'KOSHIKAKE', 'HAKO']
        KUMIKI_name = rs.GetString("Which KUMIKI to make?", None, TSUGITE_strings)

    elif KUMIKI_type == 'SHIGUCHI':
        # message
        SHIGUCHI_strings = ['TOME', 'IRIWA', 'SANMAIKUMI', 'AIKAKI', 'HAKO']
        KUMIKI_name = rs.GetString("Which KUMIKI to make?", None, SHIGUCHI_strings)

    else:
        sys.exit()

    print ('KUMIKI_name : %s' % KUMIKI_name )

    return KUMIKI_name

def get_information(KUMIKI_type):
    """Gets information to make KUMIKI.
    Receives:
        KUMIKI_type     str     Type of KUMIKI ; TSUGITE or SHIGUCHI
    Returns:
        KUMIKI_info     list    list of information
    """
    """
    # NOTE:
    Needs to get different information by type of KUMIKI ; TSUGITE, SHIGUCHI
    TSUGITE
        m_info          list    Material information ; corner points etc...
    SHIGUCHI
        m1_info         list    Material1 information
        m2_info         list    Material2 information
    """
    if KUMIKI_type == 'TSUGITE':
        m_info, m_model = get_TSUGITE_info()
        KUMIKI_info = [m_info, m_model]

    elif KUMIKI_type == 'SHIGUCHI':
        m1_info, m2_info, m1_model, m2_model, direction = get_SHIGUCHI_info()
        KUMIKI_info = [m1_info, m2_info, m1_model, m2_model, direction]

    else:
        sys.exit()

    return KUMIKI_info

def get_TSUGITE_info():
    """Gets TSUGITE information.
    Receives:
        ---
    Returns:
        m_info          list    Material information
        m_model         guid    Polysrf ; to show user what material is like
    """
    """
    # NOTE:
    # PARAMETERs
    # TSUGITE
    x_m         int     x length of material
    y_m         int     y length of material
    z_m         int     z length of material

    m_points    list    list of material points
    m_model     guid    Polysrf ; to show user what material is like
    """

    # message
    message0 = "Put the information of material to make TSUGITE."
    rs.MessageBox(message0, 0, 'Material information')

    x_m = rs.GetInteger("Put Int(mm); x length of material to make TSUGITE. (100mm ~ 500mm)")
    y_m = rs.GetInteger("Put Int(mm) ; y length of material to make TSUGITE.(30mm ~ 100mm)")

    t_m = rs.GetReal("Put Int or Real (mm) ; thickness of 1 layer to make TSUGITE\
    (2D KUMIKI is total 3 layer), (thickness of material to cut parts)")

    z_m = 3 * t_m

    layer_t_1 = t_m
    layer_t_2 = t_m
    layer_t_3 = t_m

    layer_t = [layer_t_1, layer_t_2, layer_t_3]

    m_str = 'x_m = %s' % x_m, 'y_m = %s' % y_m, 'z_m = %s' % z_m
    print (m_str)

    """
    # NOTE:
    From these Parameters ; x_m, y_m, z_m , get material corner points to make KUMIKI.
    """

    l_mp0 = left_material_point0 = (0, 0)
    l_mp1 = (0, y_m)
    r_mp0 = right_material_point0 = (x_m, 0)
    r_mp1 = (x_m, y_m)

    m_points = [l_mp0, l_mp1, r_mp0, r_mp1]

    m_info = [x_m, y_m, z_m, m_points, layer_t]

    """
    # NOTE:
    To show user what material is like, make 3D model of material.
    It has to be deleted after this code ran.
    """

    contour = [l_mp0, l_mp1, r_mp1, r_mp0, l_mp0]
    contour = rs.AddPolyline(contour)
    rs.ZoomExtents()

    start = (0, 0, 0)
    end = (0, 0, z_m)
    path = rs.AddLine(start, end)

    m_model = rs.ExtrudeCurve(contour, path)
    rs.CapPlanarHoles(m_model)
    rs.DeleteObject(path)
    rs.DeleteObject(contour)
    rs.ZoomExtents()

    return m_info, m_model

def get_SHIGUCHI_info():
    """Gets SHIGUCHI information.
    Receives:
        ---
    Returns:
        m1_info         list    Material1 information
        m2_info         list    Material2 information

        m1_model        guid    Polysrf ; to show user what material1 is like
        m2_model        guid    Polysrf ; to show user what material2 is like
        direction       str     direction to make SHIGUCHI
    """
    """
    # NOTE:
    # PARAMETERs
    x_m1        int     x length of material1
    y_m1        int     y length of material1

    x_m2        int     x length of material2
    y_m2        int     y length of material2

    z_m        int     z length of material (thickness)

    m1_points   list    list of material1 points
    m2_points   list    list of material2 points

    m1_model    guid    Polysrf ; to show user what material1 is like
    m2_model    guid    Polysrf ; to show user what material2 is like
    direction   str     direction to make SHIGUCHI
    """

    # message
    message0 = "Put the information of material1 to make SHIGUCHI."
    rs.MessageBox(message0, 0, 'Material1 information')

    x_m1 = rs.GetInteger("Put Int (mm) ; x length of material1 to make SHIGUCHI. (100mm ~ 500mm)")
    y_m1 = rs.GetInteger("Put Int (mm) ; y length of material1 to make SHIGUCHI. (30mm ~ 100mm)")

    t_m = rs.GetReal("Put Int or Real (mm) ; thickness of 1 layer to make SHIGUCHI (2D KUMIKI is total 3 layers),(thickness of material to cut parts)")

    z_m = 3 * t_m

    m1_str = 'x_m1 = %s' % x_m1, 'y_m1 = %s' % y_m1, 'z_m = %s' % z_m
    print (m1_str)

    """
    # NOTE:
    From these Parameters ; x_m1, y_m1, get material corner points to make KUMIKI.

    1   make rectangle (material1) to show user what it is like.
    """

    p0 = (0, 0)
    p1 = (0, y_m1)
    p2 = (x_m1, y_m1)
    p3 = (x_m1, 0)

    contour1 = [p0, p1, p2, p3, p0]
    contour1 = rs.AddPolyline(contour1)

    start = (0, 0, 0)
    end = (0, 0, z_m)
    path = rs.AddLine(start, end)

    m1_model = rs.ExtrudeCurve(contour1, path)
    rs.CapPlanarHoles(m1_model)
    rs.DeleteObject(path)
    rs.ZoomExtents()

    """
    2   Decides the direction to make material2
        The direction decides the material1 points (+ -).
    """
    # message
    message1 = "Choose direction to make material2."
    rs.MessageBox(message1, 0, 'Direction')

    direction_strings = ['UpperRight', 'LowerRight', 'UpperLeft', 'LowerLeft']
    direction = rs.GetString("Which direction to make the other material (material2)?",\
    None, direction_strings)

    if direction == 'UpperRight':
        m1_p0 = (0, y_m1)
        m1_p1 = (0, 0)
        m1_p2 = (x_m1, 0)
        m1_p3 = (x_m1, y_m1)

    elif direction == 'LowerRight':
        m1_p0 = (0, 0)
        m1_p1 = (0, y_m1)
        m1_p2 = (x_m1, y_m1)
        m1_p3 = (x_m1, 0)

    elif direction == 'UpperLeft':
        m1_p0 = (x_m1, y_m1)
        m1_p1 = (x_m1, 0)
        m1_p2 = (0, 0)
        m1_p3 = (0, y_m1)

    elif direction == 'LowerLeft':
        m1_p0 = (x_m1, 0)
        m1_p1 = (x_m1, y_m1)
        m1_p2 = (0, y_m1)
        m1_p3 = (0, 0)

    else:
        sys.exit()

    m1_points = [m1_p0, m1_p1, m1_p2, m1_p3]

    """
    3   Decides material2 points
    """

    x_m2 = rs.GetInteger("Put Int ; x length of material2 to make SHIGUCHI.\
    (if the size of material2 is same as material1, just put ENTER.)", y_m1, None, None)
    y_m2 = rs.GetInteger("Put Int ; y length of material2 to make SHIGUCHI.\
    (if the size of material2 is same as material2, just put EWNTER.)", x_m1, None, None)

    m2_str = 'x_m2 = %s' % x_m2, 'y_m2 = %s' % y_m2, 'z_m = %s' % z_m
    print (m2_str)

    """
    # NOTE:
    From these Parameters ; x_m2, y_m2, get material corner points to make KUMIKI.
    'm1_p3' is a base point to get material2 points.
    The direction decides the material2 points.
    """

    if direction == 'UpperRight':
        pass

    elif direction == 'LowerRight':
        y_m2 = -y_m2

    elif direction == 'UpperLeft':
        x_m2 = -x_m2

    elif direction == 'LowerLeft':
        x_m2 = -x_m2
        y_m2 = -y_m2

    else:
        sys.exit()

    dx = m1_p3[0] # NOTE: m1_p3 <- turple
    dy = m1_p3[1]

    m2_p0 = (dx, dy + y_m2)
    m2_p1 = (dx + x_m2, dy + y_m2)
    m2_p2 = (dx + x_m2, dy)
    m2_p3 = (dx, dy)

    m2_points = [m2_p0, m2_p1, m2_p2, m2_p3]

    m1_info = [x_m1, y_m1, z_m, m1_points]
    m2_info = [x_m2, y_m2, z_m, m2_points]

    """
    # NOTE:
    Make rectangle (material2) to show user what it is like.
    """
    contour2 = [m2_p0, m2_p1, m2_p2, m2_p3, m2_p0]
    contour2 = rs.AddPolyline(contour2)

    start = (0, 0, 0)
    end = (0, 0, z_m)
    path = rs.AddLine(start, end)

    m2_model = rs.ExtrudeCurve(contour2, path)
    rs.CapPlanarHoles(m2_model)
    rs.DeleteObject(path)

    rs.DeleteObject(contour1)
    rs.DeleteObject(contour2)

    rs.ZoomExtents()

    return m1_info, m2_info, m1_model, m2_model, direction

def make_KUMIKI(KUMIKI_type, KUMIKI_name, KUMIKI_info):
    """Makes selected KUMIKI 3D model to show what it is like.
    Receives:
        KUMIKI_type     str     Type of KUMIKI ; TSUGITE or SHIGUCHI

        KUMIKI_name     str     Name of KUMIKI

        KUMIKI_info     list    Information of KUMIKI to make
                                [m_info, m_model]
        m_info          list    list of material information
                                [x_m, y_m, z_m, m_points, layer_t]
        m_points        list    list of material points
                                [l_mp0, l_mp1, r_mp0, r_mp1]
    Returns:
        ---

    # NOTE:
    By KUMIKI_type and KUMIKI_name, call appropriate function.
    """

    if KUMIKI_type == 'TSUGITE':
        left_crvs, right_crvs, left_models, right_models, SEN_info =\
        make_TSUGITE(KUMIKI_name, KUMIKI_info)

        return left_crvs, right_crvs, SEN_info

    elif KUMIKI_type == 'SHIGUCHI':
        m1_crvs, m2_crvs, m1_models, m2_models, SEN_info =\
        make_SHIGUCHI(KUMIKI_name, KUMIKI_info)

        return m1_crvs, m2_crvs, SEN_info
    else:
        sys.exit()

def make_TSUGITE(KUMIKI_name, KUMIKI_info):
    """Call appropriate function from KUMIKI_name.
    Receives:
        KUMIKI_name     str     Name of KUMIKI

        KUMIKI_info     list    Information of KUMIKI to make
                                [m_info, m_model]
        m_info          list    list of material information
                                [x_m, y_m, z_m, m_points, layer_t]
        m_points        list    list of material points
                                [l_mp0, l_mp1, r_mp0, r_mp1]
    Returns:
        left_crvs       [guid]  left side crvs ; upper, middle, lower
        right_crvs      [guid]  right side crvs ; upper, middle, lower

        left_models     [guid]  left side models (Polysrf) ; upper, middle, lower
        right_models    [guid]  right side models (Polysrf) ; upper, middle, lower

        SEN_info        list    list of SEN information
    """
    """
    1   Get base point to make KUMIKI.
    """

    # message
    message = "To make KUMIKI, it needs to get base point. From base point, \
    this code makes the KUMIKI shape."

    rs.MessageBox(message, 0, 'Base Point')

    b_p = rs.GetPoint("Put the base point to make KUMIKI shape.")
    dx = b_p.X
    dy = 0 # NOTE: could be change

    """
    2   Call appropriate function. Get list of KUMIKI.
    """
    if KUMIKI_name == 'ARI':
        left_lists, right_lists, SEN_info = make_ARI(dx, dy, KUMIKI_info)

    elif KUMIKI_name == 'KAMA':
        left_lists, right_lists, SEN_info = make_KAMA(dx, dy, KUMIKI_info)

    elif KUMIKI_name == 'RYAKUKAMA':
        left_lists, right_lists, SEN_info = make_RYAKUKAMA(dx, dy, KUMIKI_info)

    elif KUMIKI_name == 'MECHIGAI':
        left_lists, right_lists, SEN_info = make_MECHIGAI(dx, dy, KUMIKI_info)

    elif KUMIKI_name == 'AIKAKI':
        left_lists, right_lists, SEN_info = make_AIKAKI_TSUGITE(dx, dy, KUMIKI_info)

    elif KUMIKI_name == 'KOSHIKAKE':
        left_lists, right_lists, SEN_info = make_KOSHIKAKE(dx, dy, KUMIKI_info)

    elif KUMIKI_name == 'HAKO':
        left_lists, right_lists, SEN_info = make_HAKO_TSUGITE(dx, dy, KUMIKI_info)

    else:
        sys.exit()

    """
    3   Make crvs (left_crvs, right_crvs)
        by 'l_n' values, the number of middle crvs to make will chabge.
    """

    m_info = KUMIKI_info[0]
    layer_t = m_info[4]
    l_n = len(layer_t)

    if l_n == 3:
        left_upper_list = left_lists[0]
        left_upper_crv = rs.AddPolyline(left_upper_list)

        left_middle_list = left_lists[1]
        left_middle_crv = rs.AddPolyline(left_middle_list)

        left_lower_list = left_lists[2]
        left_lower_crv = rs.AddPolyline(left_lower_list)

        left_crvs = [left_upper_crv, left_middle_crv, left_lower_crv]

        right_upper_list = right_lists[0]
        right_upper_crv = rs.AddPolyline(right_upper_list)

        right_middle_list = right_lists[1]
        right_middle_crv = rs.AddPolyline(right_middle_list)

        right_lower_list = right_lists[2]
        right_lower_crv = rs.AddPolyline(right_lower_list)

        right_crvs = [right_upper_crv, right_middle_crv, right_lower_crv]

    elif l_n == 4:
        left_upper_list = left_lists[0]
        left_upper_crv = rs.AddPolyline(left_upper_list)

        left_middle_list = left_lists[1]
        left_middle_crv1 = rs.AddPolyline(left_middle_list)
        left_middle_crv2 = rs.CopyObject(left_middle_crv1)

        left_lower_list = left_lists[2]
        left_lower_crv = rs.AddPolyline(left_lower_list)

        left_crvs = [left_upper_crv, left_middle_crv1, left_middle_crv2, left_lower_crv]

        right_upper_list = right_lists[0]
        right_upper_crv = rs.AddPolyline(right_upper_list)

        right_middle_list = right_lists[1]
        right_middle_crv1 = rs.AddPolyline(right_middle_list)
        right_middle_crv2 = rs.CopyObject(right_middle_crv1)

        right_lower_list = right_lists[2]
        right_lower_crv = rs.AddPolyline(right_lower_list)

        right_crvs = [right_upper_crv, right_middle_crv1, right_middle_crv2, right_lower_crv]

    elif l_n == 5:
        left_upper_list = left_lists[0]
        left_upper_crv = rs.AddPolyline(left_upper_list)

        left_middle_list = left_lists[1]
        left_middle_crv1 = rs.AddPolyline(left_middle_list)
        left_middle_crv2 = rs.CopyObject(left_middle_crv1)
        left_middle_crv3 = rs.CopyObject(left_middle_crv1)

        left_lower_list = left_lists[2]
        left_lower_crv = rs.AddPolyline(left_lower_list)

        left_crvs = [left_upper_crv, left_middle_crv1, left_middle_crv2, left_middle_crv3, left_lower_crv]

        right_upper_list = right_lists[0]
        right_upper_crv = rs.AddPolyline(right_upper_list)

        right_middle_list = right_lists[1]
        right_middle_crv1 = rs.AddPolyline(right_middle_list)
        right_middle_crv2 = rs.CopyObject(right_middle_crv1)
        right_middle_crv3 = rs.CopyObject(right_middle_crv1)

        right_lower_list = right_lists[2]
        right_lower_crv = rs.AddPolyline(right_lower_list)

        right_crvs = [right_upper_crv, right_middle_crv1, right_middle_crv2, right_middle_crv3, right_lower_crv]

    else:
        sys.exit()

    """
    4   Make 3D model.
    """

    left_models, right_models = make_TSUGITE_3D(KUMIKI_info, left_crvs, right_crvs)

    return left_crvs, right_crvs, left_models, right_models, SEN_info

def make_SHIGUCHI(KUMIKI_name, KUMIKI_info):
    """Call appropriate function from KUMIKI_name.
    Receives:
        KUMIKI_name     str     Name of KUMIKI

        KUMIKI_info     list    Information of KUMIKI to make
                                [m1_info, m2_info, m1_model, m2_model, direction]
        m1_info         list    list of material1 information
                                [x_m1, y_m1, z_m, m1_points]
        m2_info         list    list of material2 information
                                [x_m2, y_m2, z_m, m2_points]
        m1_points       list    list of material1 points
                                [m1_p0, m1_p1, m1_p2, m1_p3]
        m2_points       list    list of material2 points
                                [m2_p0, m2_p1, m2_p2, m2_p3]
    Returns:
        m1_crvs         [guid]  material1 crvs ; upper, middle, lower
                                [m1_upper_crv, m1_middle_crv, m1_lower_crv]
        m2_crvs         [guid]  material2 crvs ; upper, middle, lower
                                [m2_upper_crv, m2_middle_crv, m2_lower_crv]
        m1_models       [guid]  material1 side models (Polysrf) ; upper, middle, lower
                                [m1_upper_model, m1_middle_model, m1_lower_model]
        m2_models       [guid]  material2 side models (Polysrf) ; upper, middle, lower
                                [m2_upper_model, m2_middle_model, m2_lower_model]
        SEN_info        list    list of SEN information

    1   Base point = m1_p3
        Get parameters from list.
    """
    m1_info = KUMIKI_info[0]
    m2_info = KUMIKI_info[1]
    direction = KUMIKI_info[4]

    m1_points = m1_info[3]
    m2_points = m2_info[3]

    b_p = base_point = m1_points[3]
    dx = b_p[0]
    dy = b_p[1]

    """
    2   Call appropriate function.
    """
    if KUMIKI_name == 'TOME':
        m1_lists, m2_lists, SEN_info = make_TOME(dx, dy, KUMIKI_info)

    elif KUMIKI_name == 'IRIWA':
        m1_lists, m2_lists, SEN_info = make_IRIWA(dx, dy, KUMIKI_info)

    elif KUMIKI_name == 'SANMAIKUMI':
        m1_lists, m2_lists, SEN_info = make_SANMAIKUMI(dx, dy, KUMIKI_info)

    elif KUMIKI_name == 'AIKAKI':
        m1_lists, m2_lists, SEN_info = make_AIKAKI_KUMITE(dx, dy, KUMIKI_info)

    elif KUMIKI_name == 'HAKO':
        m1_lists, m2_lists, SEN_info = make_HAKO_KUMITE(dx, dy, KUMIKI_info)

    else:
        sys.exit()

    """
    3   Make crvs. (m1 crvs, m2 crvs)
    """

    m1_upper_list = m1_lists[0]
    m1_middle_list = m1_lists[1]
    m1_lower_list = m1_lists[2]

    m1_upper_crv = rs.AddPolyline(m1_upper_list)
    m1_middle_crv = rs.AddPolyline(m1_middle_list)
    m1_lower_crv = rs.AddPolyline(m1_lower_list)

    m2_upper_list = m2_lists[0]
    m2_middle_list = m2_lists[1]
    m2_lower_list = m2_lists[2]

    m2_upper_crv = rs.AddPolyline(m2_upper_list)
    m2_middle_crv = rs.AddPolyline(m2_middle_list)
    m2_lower_crv = rs.AddPolyline(m2_lower_list)

    m1_crvs = [m1_upper_crv, m1_middle_crv, m1_lower_crv]
    m2_crvs = [m2_upper_crv, m2_middle_crv, m2_lower_crv]

    """
    4   Make 3D model.
    """
    m1_models, m2_models = make_SHIGUCHI_3D(KUMIKI_info, m1_crvs, m2_crvs)

    return m1_crvs, m2_crvs, m1_models, m2_models, SEN_info

# KUMIKI FUNCTIONs--------------------------------------------------------------
# ------------------------------------------------------------------------------
# TSUGITE-----------------------------------------------------------------------
def make_ARI(dx, dy, KUMIKI_info):
    """Make ARI lists ; upper shape, middle shape, lower shape (3 Layers)
    Receives:
        (dx, dy)        pt      Base point to make KUMIKI

        KUMIKI_info     list    Information of KUMIKI to make
                                [m_info, m_model]
        m_info          list    list of material information
                                [x_m, y_m, z_m, m_points, layer_t]
        m_points        list    list of material points
                                [l_mp0, l_mp1, r_mp0, r_mp1]
    Returns:
        left_lists      list    list of left side points    [upper, middle, right]
        right_lists     list    list of right side points   [upper, middle, right]

        # left_crvs       [guid]  left side crvs ; upper, middle, lower
        # right_crvs      [guid]  right side crvs ; upper, middle, lower

        SEN_info        list    list of SEN information

    1   Get parameters from KUMIKI_info
    """

    m_info = KUMIKI_info[0]
    m_model = KUMIKI_info[1]

    x_m = m_info[0]
    y_m = m_info[1]
    z_m = m_info[2]
    m_points = m_info[3]

    l_mp0 = m_points[0]
    l_mp1 = m_points[1]
    r_mp0 = m_points[2]
    r_mp1 = m_points[3]

    """
    2   Get points of ARI.
    This parts could be changed.
    """
    x_k = y_m * 2 / 3               # NOTE: fixed number

    p5 = (dx, dy)
    p4 = (dx, dy + y_m / 3)
    p3 = (dx + x_k, dy + y_m / 4)
    p2 = (dx + x_k, dy + 3 * y_m / 4)
    p1 = (dx, dy + 2 * y_m / 3)
    p0 = (dx, dy + y_m)

    KUMIKI_points = [p0, p1, p2, p3, p4, p5]

    """
    3   Make temporary 3D models.
    """
    # Leftside
    left = []
    left.append(l_mp0)
    left.append(l_mp1)
    left.extend(KUMIKI_points)
    left.append(l_mp0)

    left_crv = rs.AddPolyline(left)

    # Rightside
    right = []
    right.append(r_mp0)
    right.append(r_mp1)
    right.extend(KUMIKI_points)
    right.append(r_mp0)

    right_crv = rs.AddPolyline(right)

    start = (0, 0, 0)
    end = (0, 0, z_m)
    path = rs.AddLine(start, end)

    left_model = rs.ExtrudeCurve(left_crv, path)
    right_model = rs.ExtrudeCurve(right_crv, path)

    rs.CapPlanarHoles(left_model)
    rs.CapPlanarHoles(right_model)

    rs.DeleteObject(m_model)
    rs.DeleteObject(left_crv)
    rs.DeleteObject(right_crv)

    """
    4   Get offset num.
    """
    minimum = 0
    maximum = 1.0

    offset = rs.GetReal("Put the offset num to fit KUMIKI tight. (0.0 < offset < 1.0)",\
                        0.1, minimum, maximum)

    # NOTE: offset num is not parametric number. It's always fixed.

    """
    5   Get points of ARI.
        New KUMIKI points_left -> offset num
            KUMIKI points_right -> ofset num
    """
    x_k = y_m * 2 / 3               # NOTE: fixed number

    # KUMIKI_points_left    reflect offset
    p5 = (dx, dy)
    p4 = (dx, dy + y_m / 3 - offset)
    p3 = (dx + x_k, dy + y_m / 4 - offset)
    p2 = (dx + x_k, dy + 3 * y_m / 4 + offset)
    p1 = (dx, dy + 2 * y_m / 3 + offset)
    p0 = (dx, dy + y_m)

    KUMIKI_points_left = [p0, p1, p2, p3, p4, p5]

    # KUMIKI_points_right   not reflect offset
    p5 = (dx, dy)
    p4 = (dx, dy + y_m / 3)
    p3 = (dx + x_k, dy + y_m / 4)
    p2 = (dx + x_k, dy + 3 * y_m / 4)
    p1 = (dx, dy + 2 * y_m / 3)
    p0 = (dx, dy + y_m)

    KUMIKI_points_right = [p0, p1, p2, p3, p4, p5]

    """
    6   Get SEN information to make 2D KUMIKI.
    """
    SEN_info = get_TSUGITE_SEN_info(dx, dy, KUMIKI_info, x_k)

    # upper shape
    upper_shape_left, upper_shape_right =\
    TSUGITE_make_upper_shape_points_list(dx, dy, KUMIKI_info, SEN_info)

    upper_shape_left_upper_row = upper_shape_left[0]
    upper_shape_left_lower_row = upper_shape_left[1]

    upper_shape_right_upper_row = upper_shape_right[0]
    upper_shape_right_lower_row = upper_shape_right[1]

    # lower shape
    lower_shape_left, lower_shape_right =\
    TSUGITE_make_lower_shape_points_list(dx, dy, KUMIKI_info, SEN_info)

    lower_shape_left_upper_row = lower_shape_left[0]
    lower_shape_left_lower_row = lower_shape_left[1]

    lower_shape_right_upper_row = lower_shape_right[0]
    lower_shape_right_lower_row = lower_shape_right[1]

    # middle shape
    middle_shape_left, middle_shape_right =\
    TSUGITE_make_middle_shape_points_list(dx, dy, KUMIKI_info, SEN_info)

    middle_shape_left_upper_row = middle_shape_left[0]
    middle_shape_left_lower_row = middle_shape_left[1]

    middle_shape_right_upper_row = middle_shape_right[0]
    middle_shape_right_lower_row = middle_shape_right[1]

    """
    7   Make ARI lists.
    Leftside shape & Rightside shape
    Upper_shape
    Middle_shape
    Lower_shape
    """
    # Leftside
    # Upper
    left_upper = []
    left_upper.append(l_mp0)
    left_upper.append(l_mp1)
    left_upper.extend(upper_shape_left_upper_row)

    left_upper.extend(KUMIKI_points_left)
    left_upper.extend(upper_shape_left_lower_row)
    left_upper.append(l_mp0)

    # left_upper_crv = rs.AddPolyline(left_upper)

    # Middle
    left_middle = []
    left_middle.append(l_mp0)
    left_middle.append(l_mp1)
    left_middle.extend(middle_shape_left_upper_row)

    left_middle.extend(KUMIKI_points_left)
    left_middle.extend(middle_shape_left_lower_row)
    left_middle.append(l_mp0)

    # left_middle_crv = rs.AddPolyline(left_middle)

    # Lower
    left_lower = []
    left_lower.append(l_mp0)
    left_lower.append(l_mp1)
    left_lower.extend(lower_shape_left_upper_row)

    left_lower.extend(KUMIKI_points_left)
    left_lower.extend(lower_shape_left_lower_row)
    left_lower.append(l_mp0)

    # left_lower_crv = rs.AddPolyline(left_lower)

    left_lists = [left_upper, left_middle, left_lower]

    # left_crvs = [left_upper_crv, left_middle_crv, left_lower_crv]


    # Rightside
    # Upper
    right_upper = []
    right_upper.append(r_mp0)
    right_upper.append(r_mp1)
    right_upper.extend(upper_shape_right_upper_row)

    right_upper.extend(KUMIKI_points_right)
    right_upper.extend(upper_shape_right_lower_row)
    right_upper.append(r_mp0)

    # right_upper_crv = rs.AddPolyline(right_upper)

    # Middle
    right_middle = []
    right_middle.append(r_mp0)
    right_middle.append(r_mp1)
    right_middle.extend(middle_shape_right_upper_row)

    right_middle.extend(KUMIKI_points_right)
    right_middle.extend(middle_shape_right_lower_row)
    right_middle.append(r_mp0)

    # right_middle_crv = rs.AddPolyline(right_middle)

    # Lower
    right_lower = []
    right_lower.append(r_mp0)
    right_lower.append(r_mp1)
    right_lower.extend(lower_shape_right_upper_row)

    right_lower.extend(KUMIKI_points_right)
    right_lower.extend(lower_shape_right_lower_row)
    right_lower.append(r_mp0)

    # right_lower_crv = rs.AddPolyline(right_lower)

    right_lists = [right_upper, right_middle, right_lower]

    # right_crvs = [right_upper_crv, right_middle_crv, right_lower_crv]

    rs.DeleteObjects(left_model)
    rs.DeleteObjects(right_model)


    return left_lists, right_lists, SEN_info

def make_KAMA(dx, dy, KUMIKI_info):
    """Make KAMA lists ; upper shape, middle shape, lower shape (3 Layers)
    Receives:
        (dx, dy)        pt      Base point to make KUMIKI

        KUMIKI_info     list    Information of KUMIKI to make
                                [m_info, m_model]
        m_info          list    list of material information
                                [x_m, y_m, z_m, m_points, layer_t]
        m_points        list    list of material points
                                [l_mp0, l_mp1, r_mp0, r_mp1]
    Returns:
        left_lists      list    list of left side points
        right_lists     list    list of right side points

        # left_crvs       [guid]  left side crvs ; upper, middle, lower
        # right_crvs      [guid]  right side crvs ; upper, middle, lower

        SEN_info        list    list of SEN information

    1   Get parameters from KUMIKI_info
    """

    m_info = KUMIKI_info[0]
    m_model = KUMIKI_info[1]

    x_m = m_info[0]
    y_m = m_info[1]
    z_m = m_info[2]
    m_points = m_info[3]

    l_mp0 = m_points[0]
    l_mp1 = m_points[1]
    r_mp0 = m_points[2]
    r_mp1 = m_points[3]

    """
    2   Get points of KAMA.
    This parts could be changed.
    """
    x_k = y_m                       # NOTE: fixed number

    p9 = (dx, dy)
    p8 = (dx, dy + y_m / 3)
    p7 = (dx + x_k / 2, dy + y_m / 3)
    p6 = (dx + x_k / 2, dy + y_m / 4)
    p5 = (dx + x_k, dy + y_m / 3)
    p4 = (dx + x_k, dy + 2 * y_m / 3)
    p3 = (dx + x_k / 2, dy + 3 * y_m / 4)
    p2 = (dx + x_k / 2, dy + 2 * y_m / 3)
    p1 = (dx, dy + 2 * y_m / 3)
    p0 = (dx, dy + y_m)

    KUMIKI_points = [p0, p1, p2, p3, p4, p5, p6, p7, p8, p9]

    """
    3   Make temporary 3D models.
    """
    # Leftside
    left = []
    left.append(l_mp0)
    left.append(l_mp1)
    left.extend(KUMIKI_points)
    left.append(l_mp0)

    left_crv = rs.AddPolyline(left)

    # Rightside
    right = []
    right.append(r_mp0)
    right.append(r_mp1)
    right.extend(KUMIKI_points)
    right.append(r_mp0)

    right_crv = rs.AddPolyline(right)

    start = (0, 0, 0)
    end = (0, 0, z_m)
    path = rs.AddLine(start, end)

    left_model = rs.ExtrudeCurve(left_crv, path)
    right_model = rs.ExtrudeCurve(right_crv, path)

    rs.CapPlanarHoles(left_model)
    rs.CapPlanarHoles(right_model)

    rs.DeleteObject(m_model)
    rs.DeleteObject(left_crv)
    rs.DeleteObject(right_crv)

    """
    4   Get offset num.
    """
    minimum = 0
    maximum = 1.0

    offset = rs.GetReal("Put the offset num to fit KUMIKI tight. (0.0 < offset < 1.0)",\
                        0.1, minimum, maximum)

    # NOTE: offset num is not parametric number. It's always fixed.

    """
    5   Get points of ARI.
        New KUMIKI points_left -> offset num
            KUMIKI points_right -> ofset num
    """
    x_k = y_m                       # NOTE: fixed number

    # KUMIKI_points_left    reflect offset
    p9 = (dx, dy)
    p8 = (dx, dy + y_m / 3 - offset)
    p7 = (dx + x_k / 2, dy + y_m / 3 - offset)
    p6 = (dx + x_k / 2, dy + y_m / 4 - offset)
    p5 = (dx + x_k, dy + y_m / 3 - offset)
    p4 = (dx + x_k, dy + 2 * y_m / 3 + offset)
    p3 = (dx + x_k / 2, dy + 3 * y_m / 4 + offset)
    p2 = (dx + x_k / 2, dy + 2 * y_m / 3 + offset)
    p1 = (dx, dy + 2 * y_m / 3 + offset)
    p0 = (dx, dy + y_m)

    KUMIKI_points_left = [p0, p1, p2, p3, p4, p5, p6, p7, p8, p9]

    # KUMIKI_points_right   not reflect offset
    p9 = (dx, dy)
    p8 = (dx, dy + y_m / 3)
    p7 = (dx + x_k / 2, dy + y_m / 3)
    p6 = (dx + x_k / 2, dy + y_m / 4)
    p5 = (dx + x_k, dy + y_m / 3)
    p4 = (dx + x_k, dy + 2 * y_m / 3)
    p3 = (dx + x_k / 2, dy + 3 * y_m / 4)
    p2 = (dx + x_k / 2, dy + 2 * y_m / 3)
    p1 = (dx, dy + 2 * y_m / 3)
    p0 = (dx, dy + y_m)

    KUMIKI_points_right = [p0, p1, p2, p3, p4, p5, p6, p7, p8, p9]

    """
    6   Get SEN information to make 2D KUMIKI.
    """
    SEN_info = get_TSUGITE_SEN_info(dx, dy, KUMIKI_info, x_k)

    # upper shape
    upper_shape_left, upper_shape_right =\
    TSUGITE_make_upper_shape_points_list(dx, dy, KUMIKI_info, SEN_info)

    upper_shape_left_upper_row = upper_shape_left[0]
    upper_shape_left_lower_row = upper_shape_left[1]

    upper_shape_right_upper_row = upper_shape_right[0]
    upper_shape_right_lower_row = upper_shape_right[1]

    # lower shape
    lower_shape_left, lower_shape_right =\
    TSUGITE_make_lower_shape_points_list(dx, dy, KUMIKI_info, SEN_info)

    lower_shape_left_upper_row = lower_shape_left[0]
    lower_shape_left_lower_row = lower_shape_left[1]

    lower_shape_right_upper_row = lower_shape_right[0]
    lower_shape_right_lower_row = lower_shape_right[1]

    # middle shape
    middle_shape_left, middle_shape_right =\
    TSUGITE_make_middle_shape_points_list(dx, dy, KUMIKI_info, SEN_info)

    middle_shape_left_upper_row = middle_shape_left[0]
    middle_shape_left_lower_row = middle_shape_left[1]

    middle_shape_right_upper_row = middle_shape_right[0]
    middle_shape_right_lower_row = middle_shape_right[1]

    """
    7   Make KAMA lists.
    Leftside shape & Rightside shape
    Upper_shape
    Middle_shape
    Lower_shape
    """
    # Leftside
    # Upper
    left_upper = []
    left_upper.append(l_mp0)
    left_upper.append(l_mp1)
    left_upper.extend(upper_shape_left_upper_row)

    left_upper.extend(KUMIKI_points_left)
    left_upper.extend(upper_shape_left_lower_row)
    left_upper.append(l_mp0)

    # left_upper_crv = rs.AddPolyline(left_upper)

    # Middle
    left_middle = []
    left_middle.append(l_mp0)
    left_middle.append(l_mp1)
    left_middle.extend(middle_shape_left_upper_row)

    left_middle.extend(KUMIKI_points_left)
    left_middle.extend(middle_shape_left_lower_row)
    left_middle.append(l_mp0)

    # left_middle_crv = rs.AddPolyline(left_middle)

    # Lower
    left_lower = []
    left_lower.append(l_mp0)
    left_lower.append(l_mp1)
    left_lower.extend(lower_shape_left_upper_row)

    left_lower.extend(KUMIKI_points_left)
    left_lower.extend(lower_shape_left_lower_row)
    left_lower.append(l_mp0)

    # left_lower_crv = rs.AddPolyline(left_lower)

    left_lists = [left_upper, left_middle, left_lower]

    # left_crvs = [left_upper_crv, left_middle_crv, left_lower_crv]


    # Rightside
    # Upper
    right_upper = []
    right_upper.append(r_mp0)
    right_upper.append(r_mp1)
    right_upper.extend(upper_shape_right_upper_row)

    right_upper.extend(KUMIKI_points_right)
    right_upper.extend(upper_shape_right_lower_row)
    right_upper.append(r_mp0)

    # right_upper_crv = rs.AddPolyline(right_upper)

    # Middle
    right_middle = []
    right_middle.append(r_mp0)
    right_middle.append(r_mp1)
    right_middle.extend(middle_shape_right_upper_row)

    right_middle.extend(KUMIKI_points_right)
    right_middle.extend(middle_shape_right_lower_row)
    right_middle.append(r_mp0)

    # right_middle_crv = rs.AddPolyline(right_middle)

    # Lower
    right_lower = []
    right_lower.append(r_mp0)
    right_lower.append(r_mp1)
    right_lower.extend(lower_shape_right_upper_row)

    right_lower.extend(KUMIKI_points_right)
    right_lower.extend(lower_shape_right_lower_row)
    right_lower.append(r_mp0)

    # right_lower_crv = rs.AddPolyline(right_lower)

    right_lists = [right_upper, right_middle, right_lower]

    # right_crvs = [right_upper_crv, right_middle_crv, right_lower_crv]

    rs.DeleteObjects(left_model)
    rs.DeleteObjects(right_model)

    return left_lists, right_lists, SEN_info

def make_RYAKUKAMA(dx, dy, KUMIKI_info):
    """Make RYAKUKAMA lists ; upper shape, middle shape, lower shape (3 Layers)
    Receives:
        (dx, dy)        pt      Base point to make KUMIKI

        KUMIKI_info     list    Information of KUMIKI to make
                                [m_info, m_model]
        m_info          list    list of material information
                                [x_m, y_m, z_m, m_points, layer_t]
        m_points        list    list of material points
                                [l_mp0, l_mp1, r_mp0, r_mp1]
    Returns:
        left_lists      list    list of left side points
        right_lists     list    list of right side points

        # left_crvs       [guid]  left side crvs ; upper, middle, lower
        # right_crvs      [guid]  right side crvs ; upper, middle, lower

        SEN_info        list    list of SEN information

    1   Get parameters from KUMIKI_info
    """

    m_info = KUMIKI_info[0]
    m_model = KUMIKI_info[1]

    x_m = m_info[0]
    y_m = m_info[1]
    z_m = m_info[2]
    m_points = m_info[3]

    l_mp0 = m_points[0]
    l_mp1 = m_points[1]
    r_mp0 = m_points[2]
    r_mp1 = m_points[3]

    """
    2   Get points of RYAKUKAMA.
    This parts could be changed.
    """
    x_k = 1.5 * y_m                   # NOTE: fixed number

    p5 = (dx + x_k, dy)
    p4 = (dx + x_k, dy + y_m / 5)
    p3 = (dx + 3 * x_k / 5, dy + 3 * y_m / 5)
    p2 = (dx + 2 * x_k / 5, dy + 2 * y_m / 5)
    p1 = (dx, dy + 4 * y_m / 5)
    p0 = (dx, dy + y_m)

    KUMIKI_points = [p0, p1, p2, p3, p4, p5]

    """
    3   Make temporary 3D models.
    """
    # Leftside
    left = []
    left.append(l_mp0)
    left.append(l_mp1)
    left.extend(KUMIKI_points)
    left.append(l_mp0)

    left_crv = rs.AddPolyline(left)

    # Rightside
    right = []
    right.append(r_mp0)
    right.append(r_mp1)
    right.extend(KUMIKI_points)
    right.append(r_mp0)

    right_crv = rs.AddPolyline(right)

    start = (0, 0, 0)
    end = (0, 0, z_m)
    path = rs.AddLine(start, end)

    left_model = rs.ExtrudeCurve(left_crv, path)
    right_model = rs.ExtrudeCurve(right_crv, path)

    rs.CapPlanarHoles(left_model)
    rs.CapPlanarHoles(right_model)

    rs.DeleteObject(m_model)
    rs.DeleteObject(left_crv)
    rs.DeleteObject(right_crv)

    """
    4   Get offset num.
    """
    minimum = 0
    maximum = 0.3

    offset = rs.GetReal("Put the offset num to fit KUMIKI tight. (0.0 < offset < 0.3)",\
                        0.1, minimum, maximum)

    # NOTE: offset num is not parametric number. It's always fixed.

    """
    5   Get points of ARI.
        New KUMIKI points_left -> offset num
            KUMIKI points_right -> ofset num
    """
    x_k = 1.5 * y_m                   # NOTE: fixed number

    # KUMIKI_points_left
    p5 = (dx + x_k, dy)
    p4 = (dx + x_k, dy + y_m / 5 + offset)
    p3 = (dx + 3 * x_k / 5, dy + 3 * y_m / 5 + offset)
    p2 = (dx + 2 * x_k / 5, dy + 2 * y_m / 5 + offset)
    p1 = (dx, dy + 4 * y_m / 5 + offset)
    p0 = (dx, dy + y_m)

    KUMIKI_points_left = [p0, p1, p2, p3, p4, p5]

    # KUMIKI_points_right   not reflect offset
    p5 = (dx + x_k, dy)
    p4 = (dx + x_k, dy + y_m / 5)
    p3 = (dx + 3 * x_k / 5, dy + 3 * y_m / 5)
    p2 = (dx + 2 * x_k / 5, dy + 2 * y_m / 5)
    p1 = (dx, dy + 4 * y_m / 5)
    p0 = (dx, dy + y_m)

    KUMIKI_points_right = [p0, p1, p2, p3, p4, p5]

    """
    6   Get SEN information to make 2D KUMIKI.
    """
    SEN_info = get_TSUGITE_SEN_info(dx, dy, KUMIKI_info, x_k)

    # upper shape
    upper_shape_left, upper_shape_right =\
    TSUGITE_make_upper_shape_points_list(dx, dy, KUMIKI_info, SEN_info)

    upper_shape_left_upper_row = upper_shape_left[0]
    upper_shape_left_lower_row = upper_shape_left[1]

    upper_shape_right_upper_row = upper_shape_right[0]
    upper_shape_right_lower_row = upper_shape_right[1]

    # lower shape
    lower_shape_left, lower_shape_right =\
    TSUGITE_make_lower_shape_points_list(dx, dy, KUMIKI_info, SEN_info)

    lower_shape_left_upper_row = lower_shape_left[0]
    lower_shape_left_lower_row = lower_shape_left[1]

    lower_shape_right_upper_row = lower_shape_right[0]
    lower_shape_right_lower_row = lower_shape_right[1]

    # middle shape
    middle_shape_left, middle_shape_right =\
    TSUGITE_make_middle_shape_points_list(dx, dy, KUMIKI_info, SEN_info)

    middle_shape_left_upper_row = middle_shape_left[0]
    middle_shape_left_lower_row = middle_shape_left[1]

    middle_shape_right_upper_row = middle_shape_right[0]
    middle_shape_right_lower_row = middle_shape_right[1]

    """
    7   Make RYAKUKAMA lists.
    Leftside shape & Rightside shape
    Upper_shape
    Middle_shape
    Lower_shape
    """
    # Leftside
    # Upper
    left_upper = []
    left_upper.append(l_mp0)
    left_upper.append(l_mp1)
    left_upper.extend(upper_shape_left_upper_row)

    left_upper.extend(KUMIKI_points_left)
    left_upper.extend(upper_shape_left_lower_row)
    left_upper.append(l_mp0)

    # left_upper_crv = rs.AddPolyline(left_upper)

    # Middle
    left_middle = []
    left_middle.append(l_mp0)
    left_middle.append(l_mp1)
    left_middle.extend(middle_shape_left_upper_row)

    left_middle.extend(KUMIKI_points_left)
    left_middle.extend(middle_shape_left_lower_row)
    left_middle.append(l_mp0)

    # left_middle_crv = rs.AddPolyline(left_middle)

    # Lower
    left_lower = []
    left_lower.append(l_mp0)
    left_lower.append(l_mp1)
    left_lower.extend(lower_shape_left_upper_row)

    left_lower.extend(KUMIKI_points_left)
    left_lower.extend(lower_shape_left_lower_row)
    left_lower.append(l_mp0)

    # left_lower_crv = rs.AddPolyline(left_lower)

    left_lists = [left_upper, left_middle, left_lower]

    # left_crvs = [left_upper_crv, left_middle_crv, left_lower_crv]


    # Rightside
    # Upper
    right_upper = []
    right_upper.append(r_mp0)
    right_upper.append(r_mp1)
    right_upper.extend(upper_shape_right_upper_row)

    right_upper.extend(KUMIKI_points_right)
    right_upper.extend(upper_shape_right_lower_row)
    right_upper.append(r_mp0)

    # right_upper_crv = rs.AddPolyline(right_upper)

    # Middle
    right_middle = []
    right_middle.append(r_mp0)
    right_middle.append(r_mp1)
    right_middle.extend(middle_shape_right_upper_row)

    right_middle.extend(KUMIKI_points_right)
    right_middle.extend(middle_shape_right_lower_row)
    right_middle.append(r_mp0)

    # right_middle_crv = rs.AddPolyline(right_middle)

    # Lower
    right_lower = []
    right_lower.append(r_mp0)
    right_lower.append(r_mp1)
    right_lower.extend(lower_shape_right_upper_row)

    right_lower.extend(KUMIKI_points_right)
    right_lower.extend(lower_shape_right_lower_row)
    right_lower.append(r_mp0)

    # right_lower_crv = rs.AddPolyline(right_lower)

    right_lists = [right_upper, right_middle, right_lower]

    # right_crvs = [right_upper_crv, right_middle_crv, right_lower_crv]

    rs.DeleteObjects(left_model)
    rs.DeleteObjects(right_model)

    return left_lists, right_lists, SEN_info

def make_MECHIGAI(dx, dy, KUMIKI_info):
    """Make MECHIGAI lists ; upper shape, middle shape, lower shape (3 Layers)
    Receives:
        (dx, dy)        pt      Base point to make KUMIKI

        KUMIKI_info     list    Information of KUMIKI to make
                                [m_info, m_model]
        m_info          list    list of material information
                                [x_m, y_m, z_m, m_points, layer_t]
        m_points        list    list of material points
                                [l_mp0, l_mp1, r_mp0, r_mp1]
    Returns:
        left_lists      list    list of left side information
        right_lists     list    list of right side information

        # left_crvs       [guid]  left side crvs ; upper, middle, lower
        # right_crvs      [guid]  right side crvs ; upper, middle, lower

        SEN_info        list    list of SEN information

    1   Get parameters from KUMIKI_info
    """

    m_info = KUMIKI_info[0]
    m_model = KUMIKI_info[1]

    x_m = m_info[0]
    y_m = m_info[1]
    z_m = m_info[2]
    m_points = m_info[3]

    l_mp0 = m_points[0]
    l_mp1 = m_points[1]
    r_mp0 = m_points[2]
    r_mp1 = m_points[3]

    """
    2   Get points of MECHIGAI.
    This parts could be changed.
    """
    x_k = y_m / 2 # NOTE: fixed number

    p5 = (dx, dy)
    p4 = (dx, dy + y_m / 4)
    p3 = (dx + x_k, dy + y_m / 4)
    p2 = (dx + x_k, dy + 3 * y_m / 4)
    p1 = (dx, dy + 3 * y_m / 4)
    p0 = (dx, dy + y_m)

    KUMIKI_points = [p0, p1, p2, p3, p4, p5]

    """
    3   Make temporary 3D models.
    """
    # Leftside
    left = []
    left.append(l_mp0)
    left.append(l_mp1)
    left.extend(KUMIKI_points)
    left.append(l_mp0)

    left_crv = rs.AddPolyline(left)

    # Rightside
    right = []
    right.append(r_mp0)
    right.append(r_mp1)
    right.extend(KUMIKI_points)
    right.append(r_mp0)

    right_crv = rs.AddPolyline(right)

    start = (0, 0, 0)
    end = (0, 0, z_m)
    path = rs.AddLine(start, end)

    left_model = rs.ExtrudeCurve(left_crv, path)
    right_model = rs.ExtrudeCurve(right_crv, path)

    rs.CapPlanarHoles(left_model)
    rs.CapPlanarHoles(right_model)

    rs.DeleteObject(m_model)
    rs.DeleteObject(left_crv)
    rs.DeleteObject(right_crv)

    """
    4   Get offset num.
    """
    minimum = 0
    maximum = 1.0

    offset = rs.GetReal("Put the offset num to fit KUMIKI tight. (0.0 < offset < 1.0)",\
                        0.1, minimum, maximum)

    # NOTE: offset num is not parametric number. It's always fixed.

    """
    5   Get points of ARI.
        New KUMIKI points_left -> offset num
            KUMIKI points_right -> ofset num
    """
    x_k = y_m / 2 # NOTE: fixed number

    # KUMIKI_points_left
    p5 = (dx, dy)
    p4 = (dx, dy + y_m / 4 - offset)
    p3 = (dx + x_k, dy + y_m / 4 - offset)
    p2 = (dx + x_k, dy + 3 * y_m / 4 + offset)
    p1 = (dx, dy + 3 * y_m / 4 + offset)
    p0 = (dx, dy + y_m)

    KUMIKI_points_left = [p0, p1, p2, p3, p4, p5]

    # KUMIKI_points_right   not reflect offset
    p5 = (dx, dy)
    p4 = (dx, dy + y_m / 4)
    p3 = (dx + x_k, dy + y_m / 4)
    p2 = (dx + x_k, dy + 3 * y_m / 4)
    p1 = (dx, dy + 3 * y_m / 4)
    p0 = (dx, dy + y_m)

    KUMIKI_points_right = [p0, p1, p2, p3, p4, p5]

    """
    6   Get SEN information to make 2D KUMIKI.
    """
    SEN_info = get_TSUGITE_SEN_info(dx, dy, KUMIKI_info, x_k)

    # upper shape
    upper_shape_left, upper_shape_right =\
    TSUGITE_make_upper_shape_points_list(dx, dy, KUMIKI_info, SEN_info)

    upper_shape_left_upper_row = upper_shape_left[0]
    upper_shape_left_lower_row = upper_shape_left[1]

    upper_shape_right_upper_row = upper_shape_right[0]
    upper_shape_right_lower_row = upper_shape_right[1]

    # lower shape
    lower_shape_left, lower_shape_right =\
    TSUGITE_make_lower_shape_points_list(dx, dy, KUMIKI_info, SEN_info)

    lower_shape_left_upper_row = lower_shape_left[0]
    lower_shape_left_lower_row = lower_shape_left[1]

    lower_shape_right_upper_row = lower_shape_right[0]
    lower_shape_right_lower_row = lower_shape_right[1]

    # middle shape
    middle_shape_left, middle_shape_right =\
    TSUGITE_make_middle_shape_points_list(dx, dy, KUMIKI_info, SEN_info)

    middle_shape_left_upper_row = middle_shape_left[0]
    middle_shape_left_lower_row = middle_shape_left[1]

    middle_shape_right_upper_row = middle_shape_right[0]
    middle_shape_right_lower_row = middle_shape_right[1]

    """
    7   Make MECHIGAI lists.
    Leftside shape & Rightside shape
    Upper_shape
    Middle_shape
    Lower_shape
    """
    # Leftside
    # Upper
    left_upper = []
    left_upper.append(l_mp0)
    left_upper.append(l_mp1)
    left_upper.extend(upper_shape_left_upper_row)

    left_upper.extend(KUMIKI_points_left)
    left_upper.extend(upper_shape_left_lower_row)
    left_upper.append(l_mp0)

    # left_upper_crv = rs.AddPolyline(left_upper)

    # Middle
    left_middle = []
    left_middle.append(l_mp0)
    left_middle.append(l_mp1)
    left_middle.extend(middle_shape_left_upper_row)

    left_middle.extend(KUMIKI_points_left)
    left_middle.extend(middle_shape_left_lower_row)
    left_middle.append(l_mp0)

    # left_middle_crv = rs.AddPolyline(left_middle)

    # Lower
    left_lower = []
    left_lower.append(l_mp0)
    left_lower.append(l_mp1)
    left_lower.extend(lower_shape_left_upper_row)

    left_lower.extend(KUMIKI_points_left)
    left_lower.extend(lower_shape_left_lower_row)
    left_lower.append(l_mp0)

    # left_lower_crv = rs.AddPolyline(left_lower)

    left_lists = [left_upper, left_middle, left_lower]

    # left_crvs = [left_upper_crv, left_middle_crv, left_lower_crv]


    # Rightside
    # Upper
    right_upper = []
    right_upper.append(r_mp0)
    right_upper.append(r_mp1)
    right_upper.extend(upper_shape_right_upper_row)

    right_upper.extend(KUMIKI_points_right)
    right_upper.extend(upper_shape_right_lower_row)
    right_upper.append(r_mp0)

    # right_upper_crv = rs.AddPolyline(right_upper)

    # Middle
    right_middle = []
    right_middle.append(r_mp0)
    right_middle.append(r_mp1)
    right_middle.extend(middle_shape_right_upper_row)

    right_middle.extend(KUMIKI_points_right)
    right_middle.extend(middle_shape_right_lower_row)
    right_middle.append(r_mp0)

    # right_middle_crv = rs.AddPolyline(right_middle)

    # Lower
    right_lower = []
    right_lower.append(r_mp0)
    right_lower.append(r_mp1)
    right_lower.extend(lower_shape_right_upper_row)

    right_lower.extend(KUMIKI_points_right)
    right_lower.extend(lower_shape_right_lower_row)
    right_lower.append(r_mp0)

    # right_lower_crv = rs.AddPolyline(right_lower)

    right_lists = [right_upper, right_middle, right_lower]

    # right_crvs = [right_upper_crv, right_middle_crv, right_lower_crv]

    rs.DeleteObjects(left_model)
    rs.DeleteObjects(right_model)

    return left_lists, right_lists, SEN_info

def make_AIKAKI_TSUGITE(dx, dy, KUMIKI_info):
    """Make AIKAKI lists ; upper shape, middle shape, lower shape (3 Layers)
    Receives:
        (dx, dy)        pt      Base point to make KUMIKI

        KUMIKI_info     list    Information of KUMIKI to make
                                [m_info, m_model]
        m_info          list    list of material information
                                [x_m, y_m, z_m, m_points, layer_t]
        m_points        list    list of material points
                                [l_mp0, l_mp1, r_mp0, r_mp1]
    Returns:
        left_crvs       [guid]  left side crvs ; upper, middle, lower
        right_crvs      [guid]  right side crvs ; upper, middle, lower
        SEN_info        list    list of SEN information

    1   Get parameters from KUMIKI_info
    """

    m_info = KUMIKI_info[0]
    m_model = KUMIKI_info[1]

    x_m = m_info[0]
    y_m = m_info[1]
    z_m = m_info[2]
    m_points = m_info[3]

    l_mp0 = m_points[0]
    l_mp1 = m_points[1]
    r_mp0 = m_points[2]
    r_mp1 = m_points[3]

    """
    2   Get points of AIKAKI.
    This parts could be changed.
    """
    x_k = y_m                   # NOTE: fixed number

    # left side
    l_p0 = (dx, dy + y_m)
    l_p1 = (dx, dy)

    # right side
    r_p0 = (dx + x_k, dy + y_m)
    r_p1 = (dx + x_k, dy)

    l_KUMIKI_points = [l_p0, l_p1]
    r_KUMIKI_points = [r_p0, r_p1]

    """
    3   Make temporary 3D models.
    """
    # Make crvs
    # Leftside
    # Upper
    left_upper = []
    left_upper.append(l_mp0)
    left_upper.append(l_mp1)
    left_upper.extend(l_KUMIKI_points)
    left_upper.append(l_mp0)

    left_upper_crv = rs.AddPolyline(left_upper)

    # Lower
    left_lower = []
    left_lower.append(l_mp0)
    left_lower.append(l_mp1)
    left_lower.extend(r_KUMIKI_points)
    left_lower.append(l_mp0)

    left_lower_crv = rs.AddPolyline(left_lower)

    # Rightside
    # Upper
    right_upper = []
    right_upper.append(r_mp0)
    right_upper.append(r_mp1)
    right_upper.extend(l_KUMIKI_points)
    right_upper.append(r_mp0)

    right_upper_crv = rs.AddPolyline(right_upper)

    # Lower
    right_lower = []
    right_lower.append(r_mp0)
    right_lower.append(r_mp1)
    right_lower.extend(r_KUMIKI_points)
    right_lower.append(r_mp0)

    right_lower_crv = rs.AddPolyline(right_lower)

    # Extrude
    start = (0, 0, 0)
    end = (0, 0, z_m / 3)
    path_1layer = rs.AddLine(start, end)

    start = (0, 0, 0)
    end = (0, 0, 2 * z_m / 3)
    path_2layer = rs.AddLine(start, end)

    left_upper_model = rs.ExtrudeCurve(left_upper_crv, path_1layer)
    right_upper_model = rs.ExtrudeCurve(right_upper_crv, path_1layer)

    left_lower_model = rs.ExtrudeCurve(left_lower_crv, path_2layer)
    right_lower_model = rs.ExtrudeCurve(right_lower_crv, path_2layer)

    rs.CapPlanarHoles(left_upper_model)
    rs.CapPlanarHoles(right_upper_model)

    rs.CapPlanarHoles(left_lower_model)
    rs.CapPlanarHoles(right_lower_model)

    # Deploy
    trans = (0, 0, 2 * z_m / 3)
    rs.MoveObject(left_upper_model, trans)
    rs.MoveObject(right_upper_model, trans)

    rs.DeleteObject(m_model)
    rs.DeleteObject(left_upper_crv)
    rs.DeleteObject(left_lower_crv)
    rs.DeleteObject(right_upper_crv)
    rs.DeleteObject(right_lower_crv)

    """
    4   Get SEN information to make 2D KUMIKI.
    """
    SEN_info = get_TSUGITE_SEN_info(dx, dy, KUMIKI_info, x_k)

    # upper shape
    upper_shape_left, upper_shape_right =\
    TSUGITE_make_upper_shape_points_list(dx, dy, KUMIKI_info, SEN_info)

    upper_shape_left_upper_row = upper_shape_left[0]
    upper_shape_left_lower_row = upper_shape_left[1]

    upper_shape_right_upper_row = upper_shape_right[0]
    upper_shape_right_lower_row = upper_shape_right[1]

    # lower shape
    lower_shape_left, lower_shape_right =\
    TSUGITE_make_lower_shape_points_list(dx, dy, KUMIKI_info, SEN_info)

    lower_shape_left_upper_row = lower_shape_left[0]
    lower_shape_left_lower_row = lower_shape_left[1]

    lower_shape_right_upper_row = lower_shape_right[0]
    lower_shape_right_lower_row = lower_shape_right[1]

    # middle shape
    middle_shape_left, middle_shape_right =\
    TSUGITE_make_middle_shape_points_list(dx, dy, KUMIKI_info, SEN_info)

    middle_shape_left_upper_row = middle_shape_left[0]
    middle_shape_left_lower_row = middle_shape_left[1]

    middle_shape_right_upper_row = middle_shape_right[0]
    middle_shape_right_lower_row = middle_shape_right[1]

    """
    5   Make AIKAKI lists.
    Leftside shape & Rightside shape
    Upper_shape     -> l_KUMIKI_points
    Middle_shape    -> r_KUMIKI_points
    Lower_shape     -> r_KUMIKI_points
    """
    # Leftside
    # Upper
    left_upper = []
    left_upper.append(l_mp0)
    left_upper.append(l_mp1)
    left_upper.extend(upper_shape_left_upper_row)

    left_upper.extend(l_KUMIKI_points)
    left_upper.extend(upper_shape_left_lower_row)
    left_upper.append(l_mp0)

    # left_upper_crv = rs.AddPolyline(left_upper)

    # Middle
    left_middle = []
    left_middle.append(l_mp0)
    left_middle.append(l_mp1)
    left_middle.extend(middle_shape_left_upper_row)

    left_middle.extend(r_KUMIKI_points)
    left_middle.extend(middle_shape_left_lower_row)
    left_middle.append(l_mp0)

    # left_middle_crv = rs.AddPolyline(left_middle)

    # Lower
    left_lower = []
    left_lower.append(l_mp0)
    left_lower.append(l_mp1)
    left_lower.extend(lower_shape_left_upper_row)

    left_lower.extend(r_KUMIKI_points)
    left_lower.extend(lower_shape_left_lower_row)
    left_lower.append(l_mp0)

    # left_lower_crv = rs.AddPolyline(left_lower)

    left_lists = [left_upper, left_middle, left_lower]

    # left_crvs = [left_upper_crv, left_middle_crv, left_lower_crv]


    # Rightside
    # Upper
    right_upper = []
    right_upper.append(r_mp0)
    right_upper.append(r_mp1)
    right_upper.extend(upper_shape_right_upper_row)

    right_upper.extend(l_KUMIKI_points)
    right_upper.extend(upper_shape_right_lower_row)
    right_upper.append(r_mp0)

    # right_upper_crv = rs.AddPolyline(right_upper)

    # Middle
    right_middle = []
    right_middle.append(r_mp0)
    right_middle.append(r_mp1)
    right_middle.extend(middle_shape_right_upper_row)

    right_middle.extend(r_KUMIKI_points)
    right_middle.extend(middle_shape_right_lower_row)
    right_middle.append(r_mp0)

    # right_middle_crv = rs.AddPolyline(right_middle)

    # Lower
    right_lower = []
    right_lower.append(r_mp0)
    right_lower.append(r_mp1)
    right_lower.extend(lower_shape_right_upper_row)

    right_lower.extend(r_KUMIKI_points)
    right_lower.extend(lower_shape_right_lower_row)
    right_lower.append(r_mp0)

    # right_lower_crv = rs.AddPolyline(right_lower)

    right_lists = [right_upper, right_middle, right_lower]

    # right_crvs = [right_upper_crv, right_middle_crv, right_lower_crv]

    rs.DeleteObjects(left_upper_model)
    rs.DeleteObjects(left_lower_model)
    rs.DeleteObjects(right_upper_model)
    rs.DeleteObjects(right_lower_model)

    return left_lists, right_lists, SEN_info

def make_KOSHIKAKE(dx, dy, KUMIKI_info):
    """Make KOSHIKAKE lists ; upper shape, middle shape, lower shape (3 Layers)
    Receives:
        (dx, dy)        pt      Base point to make KUMIKI

        KUMIKI_info     list    Information of KUMIKI to make
                                [m_info, m_model]
        m_info          list    list of material information
                                [x_m, y_m, z_m, m_points, layer_t]
        m_points        list    list of material points
                                [l_mp0, l_mp1, r_mp0, r_mp1]
    Returns:
        left_crvs       [guid]  left side crvs ; upper, middle, lower
        right_crvs      [guid]  right side crvs ; upper, middle, lower
        SEN_info        list    list of SEN information

    1   Get parameters from KUMIKI_info
    """

    m_info = KUMIKI_info[0]
    m_model = KUMIKI_info[1]

    x_m = m_info[0]
    y_m = m_info[1]
    z_m = m_info[2]
    m_points = m_info[3]

    l_mp0 = m_points[0]
    l_mp1 = m_points[1]
    r_mp0 = m_points[2]
    r_mp1 = m_points[3]

    """
    2   Get points of KOSHIKAKE.
    This parts could be changed.
    """
    x_k = y_m / 3                   # NOTE: fixed number

    # left side
    l_p0 = (dx, dy + y_m)
    l_p1 = (dx, dy)

    # right side
    r_p0 = (dx + x_k, dy + y_m)
    r_p1 = (dx + x_k, dy)

    l_KUMIKI_points = [l_p0, l_p1]
    r_KUMIKI_points = [r_p0, r_p1]

    """
    3   Make temporary 3D models.
    """
    # Make crvs
    # Leftside
    # Upper
    left_upper = []
    left_upper.append(l_mp0)
    left_upper.append(l_mp1)
    left_upper.extend(l_KUMIKI_points)
    left_upper.append(l_mp0)

    left_upper_crv = rs.AddPolyline(left_upper)

    # Lower
    left_lower = []
    left_lower.append(l_mp0)
    left_lower.append(l_mp1)
    left_lower.extend(r_KUMIKI_points)
    left_lower.append(l_mp0)

    left_lower_crv = rs.AddPolyline(left_lower)

    # Rightside
    # Upper
    right_upper = []
    right_upper.append(r_mp0)
    right_upper.append(r_mp1)
    right_upper.extend(l_KUMIKI_points)
    right_upper.append(r_mp0)

    right_upper_crv = rs.AddPolyline(right_upper)

    # Lower
    right_lower = []
    right_lower.append(r_mp0)
    right_lower.append(r_mp1)
    right_lower.extend(r_KUMIKI_points)
    right_lower.append(r_mp0)

    right_lower_crv = rs.AddPolyline(right_lower)

    # Extrude
    start = (0, 0, 0)
    end = (0, 0, z_m / 3)
    path_1layer = rs.AddLine(start, end)

    start = (0, 0, 0)
    end = (0, 0, 2 * z_m / 3)
    path_2layer = rs.AddLine(start, end)

    left_upper_model = rs.ExtrudeCurve(left_upper_crv, path_2layer)
    right_upper_model = rs.ExtrudeCurve(right_upper_crv, path_2layer)

    left_lower_model = rs.ExtrudeCurve(left_lower_crv, path_1layer)
    right_lower_model = rs.ExtrudeCurve(right_lower_crv, path_1layer)

    rs.CapPlanarHoles(left_upper_model)
    rs.CapPlanarHoles(right_upper_model)

    rs.CapPlanarHoles(left_lower_model)
    rs.CapPlanarHoles(right_lower_model)

    # Deploy
    trans = (0, 0, z_m / 3)
    rs.MoveObject(left_upper_model, trans)
    rs.MoveObject(right_upper_model, trans)

    rs.DeleteObject(m_model)
    rs.DeleteObject(left_upper_crv)
    rs.DeleteObject(left_lower_crv)
    rs.DeleteObject(right_upper_crv)
    rs.DeleteObject(right_lower_crv)

    """
    4   Get SEN information to make 2D KUMIKI.
    """
    SEN_info = get_TSUGITE_SEN_info(dx, dy, KUMIKI_info, x_k)

    # upper shape
    upper_shape_left, upper_shape_right =\
    TSUGITE_make_upper_shape_points_list(dx, dy, KUMIKI_info, SEN_info)

    upper_shape_left_upper_row = upper_shape_left[0]
    upper_shape_left_lower_row = upper_shape_left[1]

    upper_shape_right_upper_row = upper_shape_right[0]
    upper_shape_right_lower_row = upper_shape_right[1]

    # lower shape
    lower_shape_left, lower_shape_right =\
    TSUGITE_make_lower_shape_points_list(dx, dy, KUMIKI_info, SEN_info)

    lower_shape_left_upper_row = lower_shape_left[0]
    lower_shape_left_lower_row = lower_shape_left[1]

    lower_shape_right_upper_row = lower_shape_right[0]
    lower_shape_right_lower_row = lower_shape_right[1]

    # middle shape
    middle_shape_left, middle_shape_right =\
    TSUGITE_make_middle_shape_points_list(dx, dy, KUMIKI_info, SEN_info)

    middle_shape_left_upper_row = middle_shape_left[0]
    middle_shape_left_lower_row = middle_shape_left[1]

    middle_shape_right_upper_row = middle_shape_right[0]
    middle_shape_right_lower_row = middle_shape_right[1]

    """
    5   Make KOSHIKAKE lists.
    Leftside shape & Rightside shape
    Upper_shape     -> l_KUMIKI_points
    Middle_shape    -> l_KUMIKI_points
    Lower_shape     -> r_KUMIKI_points
    """
    # Leftside
    # Upper
    left_upper = []
    left_upper.append(l_mp0)
    left_upper.append(l_mp1)
    left_upper.extend(upper_shape_left_upper_row)

    left_upper.extend(l_KUMIKI_points)
    left_upper.extend(upper_shape_left_lower_row)
    left_upper.append(l_mp0)

    # left_upper_crv = rs.AddPolyline(left_upper)

    # Middle
    left_middle = []
    left_middle.append(l_mp0)
    left_middle.append(l_mp1)
    left_middle.extend(middle_shape_left_upper_row)

    left_middle.extend(l_KUMIKI_points)
    left_middle.extend(middle_shape_left_lower_row)
    left_middle.append(l_mp0)

    # left_middle_crv = rs.AddPolyline(left_middle)

    # Lower
    left_lower = []
    left_lower.append(l_mp0)
    left_lower.append(l_mp1)
    left_lower.extend(lower_shape_left_upper_row)

    left_lower.extend(r_KUMIKI_points)
    left_lower.extend(lower_shape_left_lower_row)
    left_lower.append(l_mp0)

    # left_lower_crv = rs.AddPolyline(left_lower)

    left_lists = [left_upper, left_middle, left_lower]

    # left_crvs = [left_upper_crv, left_middle_crv, left_lower_crv]

    # Rightside
    # Upper
    right_upper = []
    right_upper.append(r_mp0)
    right_upper.append(r_mp1)
    right_upper.extend(upper_shape_right_upper_row)

    right_upper.extend(l_KUMIKI_points)
    right_upper.extend(upper_shape_right_lower_row)
    right_upper.append(r_mp0)

    # right_upper_crv = rs.AddPolyline(right_upper)

    # Middle
    right_middle = []
    right_middle.append(r_mp0)
    right_middle.append(r_mp1)
    right_middle.extend(middle_shape_right_upper_row)

    right_middle.extend(l_KUMIKI_points)
    right_middle.extend(middle_shape_right_lower_row)
    right_middle.append(r_mp0)

    # right_middle_crv = rs.AddPolyline(right_middle)

    # Lower
    right_lower = []
    right_lower.append(r_mp0)
    right_lower.append(r_mp1)
    right_lower.extend(lower_shape_right_upper_row)

    right_lower.extend(r_KUMIKI_points)
    right_lower.extend(lower_shape_right_lower_row)
    right_lower.append(r_mp0)

    # right_lower_crv = rs.AddPolyline(right_lower)

    right_lists = [right_upper, right_middle, right_lower]

    # right_crvs = [right_upper_crv, right_middle_crv, right_lower_crv]

    rs.DeleteObject(m_model)
    rs.DeleteObjects(left_upper_model)
    rs.DeleteObjects(left_lower_model)
    rs.DeleteObjects(right_upper_model)
    rs.DeleteObjects(right_lower_model)

    return left_lists, right_lists, SEN_info

def make_HAKO_TSUGITE(dx, dy, KUMIKI_info):
    """Make HAKO lists ; upper shape, middle shape, lower shape (3 Layers)
    Receives:
        (dx, dy)        pt      Base point to make KUMIKI

        KUMIKI_info     list    Information of KUMIKI to make
                                [m_info, m_model]
        m_info          list    list of material information
                                [x_m, y_m, z_m, m_points, layer_t]
        m_points        list    list of material points
                                [l_mp0, l_mp1, r_mp0, r_mp1]
    Returns:
        left_crvs       [guid]  left side crvs ; upper, middle, lower
        right_crvs      [guid]  right side crvs ; upper, middle, lower
        SEN_info        list    list of SEN information

    1   Get parameters from KUMIKI_info
    """

    m_info = KUMIKI_info[0]
    m_model = KUMIKI_info[1]

    x_m = m_info[0]
    y_m = m_info[1]
    z_m = m_info[2]
    m_points = m_info[3]

    l_mp0 = m_points[0]
    l_mp1 = m_points[1]
    r_mp0 = m_points[2]
    r_mp1 = m_points[3]

    """
    2   Get points of HAKO.
    This parts could be changed.
    """
    x_k = y_m                       # NOTE: fixed number

    p0 = (dx, dy + y_m)
    p1 = (dx, dy + 2 * y_m / 3)
    p2 = (dx + x_k, dy + 2 * y_m / 3)
    p3 = (dx + x_k, 0)
    p4 = (dx, dy)

    KUMIKI_points1 = [p0, p1, p2, p3, p4]  # NOTE: complex shape
    KUMIKI_points2 = [p0, p4]              # NOTE: line shape
    KUMIKI_points3 = KUMIKI_points1[:-1]

    """
    3   Make temporary 3D models.
    """
    # Make crvs
    # Leftside
    # Upper
    left_upper = []
    left_upper.append(l_mp0)
    left_upper.append(l_mp1)
    left_upper.extend(KUMIKI_points1)
    left_upper.append(l_mp0)

    left_upper_crv = rs.AddPolyline(left_upper)

    # Lower
    left_lower = []
    left_lower.append(l_mp0)
    left_lower.append(l_mp1)
    left_lower.extend(KUMIKI_points2)
    left_lower.append(l_mp0)

    left_lower_crv = rs.AddPolyline(left_lower)

    # Rightside
    # Upper
    right_upper = []
    right_upper.append(r_mp0)
    right_upper.append(r_mp1)
    right_upper.extend(KUMIKI_points3)
    right_upper.append(r_mp0)

    right_upper_crv = rs.AddPolyline(right_upper)

    # Lower
    right_lower = []
    right_lower.append(r_mp0)
    right_lower.append(r_mp1)
    right_lower.extend(KUMIKI_points2)
    right_lower.append(r_mp0)

    right_lower_crv = rs.AddPolyline(right_lower)

    # Extrude
    start = (0, 0, 0)
    end = (0, 0, z_m / 3)
    path_1layer = rs.AddLine(start, end)

    start = (0, 0, 0)
    end = (0, 0, 2 * z_m / 3)
    path_2layer = rs.AddLine(start, end)

    left_upper_model = rs.ExtrudeCurve(left_upper_crv, path_2layer)
    right_upper_model = rs.ExtrudeCurve(right_upper_crv, path_2layer)

    left_lower_model = rs.ExtrudeCurve(left_lower_crv, path_1layer)
    right_lower_model = rs.ExtrudeCurve(right_lower_crv, path_1layer)

    rs.CapPlanarHoles(left_upper_model)
    rs.CapPlanarHoles(right_upper_model)

    rs.CapPlanarHoles(left_lower_model)
    rs.CapPlanarHoles(right_lower_model)

    # Deploy
    trans = (0, 0, z_m / 3)
    rs.MoveObject(left_upper_model, trans)
    rs.MoveObject(right_upper_model, trans)

    rs.DeleteObject(m_model)
    rs.DeleteObject(left_upper_crv)
    rs.DeleteObject(left_lower_crv)
    rs.DeleteObject(right_upper_crv)
    rs.DeleteObject(right_lower_crv)

    """
    4   Get SEN information to make 2D KUMIKI.
    """
    SEN_info = get_TSUGITE_SEN_info(dx, dy, KUMIKI_info, x_k)

    # upper shape
    upper_shape_left, upper_shape_right =\
    TSUGITE_make_upper_shape_points_list(dx, dy, KUMIKI_info, SEN_info)

    upper_shape_left_upper_row = upper_shape_left[0]
    upper_shape_left_lower_row = upper_shape_left[1]

    upper_shape_right_upper_row = upper_shape_right[0]
    upper_shape_right_lower_row = upper_shape_right[1]

    # lower shape
    lower_shape_left, lower_shape_right =\
    TSUGITE_make_lower_shape_points_list(dx, dy, KUMIKI_info, SEN_info)

    lower_shape_left_upper_row = lower_shape_left[0]
    lower_shape_left_lower_row = lower_shape_left[1]

    lower_shape_right_upper_row = lower_shape_right[0]
    lower_shape_right_lower_row = lower_shape_right[1]

    # middle shape
    middle_shape_left, middle_shape_right =\
    TSUGITE_make_middle_shape_points_list(dx, dy, KUMIKI_info, SEN_info)

    middle_shape_left_upper_row = middle_shape_left[0]
    middle_shape_left_lower_row = middle_shape_left[1]

    middle_shape_right_upper_row = middle_shape_right[0]
    middle_shape_right_lower_row = middle_shape_right[1]

    """
    5   Make HAKO lists.
    Leftside shape & Rightside shape
    Upper_shape     -> KUMIKI_points1
    Middle_shape    -> KUMIKI_points1
    Lower_shape     -> KUMIKI_points2
    """
    # Leftside
    # Upper
    left_upper = []
    left_upper.append(l_mp0)
    left_upper.append(l_mp1)
    left_upper.extend(upper_shape_left_upper_row)

    left_upper.extend(KUMIKI_points1)
    left_upper.extend(upper_shape_left_lower_row)
    left_upper.append(l_mp0)

    # left_upper_crv = rs.AddPolyline(left_upper)

    # Middle
    left_middle = []
    left_middle.append(l_mp0)
    left_middle.append(l_mp1)
    left_middle.extend(middle_shape_left_upper_row)

    left_middle.extend(KUMIKI_points1)
    left_middle.extend(middle_shape_left_lower_row)
    left_middle.append(l_mp0)

    # left_middle_crv = rs.AddPolyline(left_middle)

    # Lower
    left_lower = []
    left_lower.append(l_mp0)
    left_lower.append(l_mp1)
    left_lower.extend(lower_shape_left_upper_row)

    left_lower.extend(KUMIKI_points2)
    left_lower.extend(lower_shape_left_lower_row)
    left_lower.append(l_mp0)

    # left_lower_crv = rs.AddPolyline(left_lower)

    left_lists = [left_upper, left_middle, left_lower]

    # left_crvs = [left_upper_crv, left_middle_crv, left_lower_crv]

    # Rightside
    """
    # WARNING:
    odd revise
    Have to reduce last elements(pt) from KUMIKI_point1
    Rename list as KUMIKI_points3
    """

    KUMIKI_points3 = KUMIKI_points1[:-1]

    # Upper
    right_upper = []
    right_upper.append(r_mp0)
    right_upper.append(r_mp1)
    right_upper.extend(upper_shape_right_upper_row)

    right_upper.extend(KUMIKI_points3)
    right_upper.extend(upper_shape_right_lower_row)
    right_upper.append(r_mp0)

    # right_upper_crv = rs.AddPolyline(right_upper)

    # Middle
    right_middle = []
    right_middle.append(r_mp0)
    right_middle.append(r_mp1)
    right_middle.extend(middle_shape_right_upper_row)

    right_middle.extend(KUMIKI_points3)
    right_middle.extend(middle_shape_right_lower_row)
    right_middle.append(r_mp0)

    # right_middle_crv = rs.AddPolyline(right_middle)

    # Lower
    right_lower = []
    right_lower.append(r_mp0)
    right_lower.append(r_mp1)
    right_lower.extend(lower_shape_right_upper_row)

    right_lower.extend(KUMIKI_points2)
    right_lower.extend(lower_shape_right_lower_row)
    right_lower.append(r_mp0)

    # right_lower_crv = rs.AddPolyline(right_lower)

    right_lists = [right_upper, right_middle, right_lower]

    # right_crvs = [right_upper_crv, right_middle_crv, right_lower_crv]

    rs.DeleteObject(m_model)
    rs.DeleteObjects(left_upper_model)
    rs.DeleteObjects(left_lower_model)
    rs.DeleteObjects(right_upper_model)
    rs.DeleteObjects(right_lower_model)

    return left_lists, right_lists, SEN_info

# TSUGITE 3D modeller-----------------------------------------------------------
def make_TSUGITE_3D(KUMIKI_info, left_crvs, right_crvs):
    """Make TSUGITE 3D model to show user what it is like.
    Receives:
        KUMIKI_info     list    Information of KUMIKI to make
                                [m_info, m_model]
        m_info          list    list of material information
                                [x_m, y_m, z_
                                m, m_points, layer_t]
        left_crvs       [guid]  left side crvs ; upper, middle, lower
                                [left_upper_crv, left_middle_crv, left_lower_crv]

        right_crvs      [guid]  right side crvs ; upper, middle, lower
                                [right_upper_crv, right_middle_crv, right_lower_crv]
    Returns:
        left_models     [guid]  left side models (Polysrf) ; upper, middle, lower
        right_models    [guid]  right side models (Polysrf) ; upper, middle, lower

    1   Get parameter and objects from list.
    """
    m_info = KUMIKI_info[0]
    x_m = m_info[0]
    y_m = m_info[1]
    z_m = m_info[2]

    layer_t = m_info[4]

    l_n = number_of_layers = len(layer_t)

    """
    # NOTE:
    By 'l_n' values, the number of middle shape will change.

    # 3 <= l_n <= 5
    """

    if l_n == 3:
        layer_t_1 = layer_t[0]
        layer_t_2 = layer_t[1]
        layer_t_3 = layer_t[2]

        left_upper_crv = left_crvs[0]
        left_middle_crv = left_crvs[1]
        left_lower_crv = left_crvs[2]

        right_upper_crv = right_crvs[0]
        right_middle_crv = right_crvs[1]
        right_lower_crv = right_crvs[2]

        """
        2   Extrude Crvs.
        """

        start = (0, 0, 0)
        end = (0, 0, layer_t_1)
        path_upper = rs.AddLine(start, end)

        start = (0, 0, 0)
        end = (0, 0, layer_t_2)
        path_middle = rs.AddLine(start, end)

        start = (0, 0, 0)
        end = (0, 0, layer_t_3)
        path_lower = rs.AddLine(start, end)

        # Leftside
        left_upper_model = rs.ExtrudeCurve(left_upper_crv, path_upper)
        left_middle_model = rs.ExtrudeCurve(left_middle_crv, path_middle)
        left_lower_model = rs.ExtrudeCurve(left_lower_crv, path_lower)

        rs.CapPlanarHoles(left_upper_model)
        rs.CapPlanarHoles(left_middle_model)
        rs.CapPlanarHoles(left_lower_model)

        # Rightside
        right_upper_model = rs.ExtrudeCurve(right_upper_crv, path_upper)
        right_middle_model = rs.ExtrudeCurve(right_middle_crv, path_middle)
        right_lower_model = rs.ExtrudeCurve(right_lower_crv, path_lower)

        rs.CapPlanarHoles(right_upper_model)
        rs.CapPlanarHoles(right_middle_model)
        rs.CapPlanarHoles(right_lower_model)

        """
        3   Deploy Polysrf.
        """
        trans_upper = (0, 0, layer_t_2 + layer_t_3)
        rs.MoveObjects([left_upper_model, right_upper_model], trans_upper)

        trans_middle = (0, 0, layer_t_3)
        rs.MoveObjects([left_middle_model, right_middle_model], trans_middle)


        left_models = [left_upper_model, left_middle_model, left_lower_model]
        right_models = [right_upper_model, right_middle_model, right_lower_model]

        rs.DeleteObject(path_upper)
        rs.DeleteObject(path_middle)
        rs.DeleteObject(path_lower)


    elif l_n == 4:
        layer_t_1 = layer_t[0]
        layer_t_2 = layer_t[1]
        layer_t_3 = layer_t[2]
        layer_t_4 = layer_t[3]

        left_upper_crv = left_crvs[0]
        left_middle_crv1 = left_crvs[1]
        left_middle_crv2 = left_crvs[2]
        left_lower_crv = left_crvs[3]

        right_upper_crv = right_crvs[0]
        right_middle_crv1 = right_crvs[1]
        right_middle_crv2 = right_crvs[2]
        right_lower_crv = right_crvs[3]

        """
        2   Extrude Crvs.
        """

        start = (0, 0, 0)
        end = (0, 0, layer_t_1)
        path_upper = rs.AddLine(start, end)

        start = (0, 0, 0)
        end = (0, 0, layer_t_2)
        path_middle1 = rs.AddLine(start, end)

        start = (0, 0, 0)
        end = (0, 0, layer_t_3)
        path_middle2 = rs.AddLine(start, end)

        start = (0, 0, 0)
        end = (0, 0, layer_t_4)
        path_lower = rs.AddLine(start, end)

        # Leftside
        left_upper_model = rs.ExtrudeCurve(left_upper_crv, path_upper)
        left_middle_model1 = rs.ExtrudeCurve(left_middle_crv1, path_middle1)
        left_middle_model2 = rs.ExtrudeCurve(left_middle_crv2, path_middle2)
        left_lower_model = rs.ExtrudeCurve(left_lower_crv, path_lower)

        rs.CapPlanarHoles(left_upper_model)
        rs.CapPlanarHoles(left_middle_model1)
        rs.CapPlanarHoles(left_middle_model2)
        rs.CapPlanarHoles(left_lower_model)

        # Rightside
        right_upper_model = rs.ExtrudeCurve(right_upper_crv, path_upper)
        right_middle_model1 = rs.ExtrudeCurve(right_middle_crv1, path_middle1)
        right_middle_model2 = rs.ExtrudeCurve(right_middle_crv2, path_middle2)
        right_lower_model = rs.ExtrudeCurve(right_lower_crv, path_lower)

        rs.CapPlanarHoles(right_upper_model)
        rs.CapPlanarHoles(right_middle_model1)
        rs.CapPlanarHoles(right_middle_model2)
        rs.CapPlanarHoles(right_lower_model)

        """
        3   Deploy Polysrf.
        """
        trans_upper = (0, 0, layer_t_2 + layer_t_3 + layer_t_4)
        rs.MoveObjects([left_upper_model, right_upper_model], trans_upper)

        trans_middle1 = (0, 0, layer_t_3 + layer_t_4)
        rs.MoveObjects([left_middle_model1, right_middle_model1], trans_middle1)

        trans_middle2 = (0, 0, layer_t_4)
        rs.MoveObjects([left_middle_model2, right_middle_model2], trans_middle2)


        left_models = [left_upper_model, left_middle_model1, left_middle_model2, left_lower_model]
        right_models = [right_upper_model, right_middle_model1, right_middle_model2, right_lower_model]

        rs.DeleteObject(path_upper)
        rs.DeleteObject(path_middle1)
        rs.DeleteObject(path_middle2)
        rs.DeleteObject(path_lower)

    elif l_n == 5:
        layer_t_1 = layer_t[0]
        layer_t_2 = layer_t[1]
        layer_t_3 = layer_t[2]
        layer_t_4 = layer_t[3]
        layer_t_5 = layer_t[4]

        left_upper_crv = left_crvs[0]
        left_middle_crv1 = left_crvs[1]
        left_middle_crv2 = left_crvs[2]
        left_middle_crv3 = left_crvs[3]
        left_lower_crv = left_crvs[4]

        right_upper_crv = right_crvs[0]
        right_middle_crv1 = right_crvs[1]
        right_middle_crv2 = right_crvs[2]
        right_middle_crv3 = right_crvs[3]
        right_lower_crv = right_crvs[4]

        """
        2   Extrude Crvs.
        """

        start = (0, 0, 0)
        end = (0, 0, layer_t_1)
        path_upper = rs.AddLine(start, end)

        start = (0, 0, 0)
        end = (0, 0, layer_t_2)
        path_middle1 = rs.AddLine(start, end)

        start = (0, 0, 0)
        end = (0, 0, layer_t_3)
        path_middle2 = rs.AddLine(start, end)

        start = (0, 0, 0)
        end = (0, 0, layer_t_4)
        path_middle3 = rs.AddLine(start, end)

        start = (0, 0, 0)
        end = (0, 0, layer_t_5)
        path_lower = rs.AddLine(start, end)

        # Leftside
        left_upper_model = rs.ExtrudeCurve(left_upper_crv, path_upper)
        left_middle_model1 = rs.ExtrudeCurve(left_middle_crv1, path_middle1)
        left_middle_model2 = rs.ExtrudeCurve(left_middle_crv2, path_middle2)
        left_middle_model3 = rs.ExtrudeCurve(left_middle_crv3, path_middle3)
        left_lower_model = rs.ExtrudeCurve(left_lower_crv, path_lower)

        rs.CapPlanarHoles(left_upper_model)
        rs.CapPlanarHoles(left_middle_model1)
        rs.CapPlanarHoles(left_middle_model2)
        rs.CapPlanarHoles(left_middle_model3)
        rs.CapPlanarHoles(left_lower_model)

        # Rightside
        right_upper_model = rs.ExtrudeCurve(right_upper_crv, path_upper)
        right_middle_model1 = rs.ExtrudeCurve(right_middle_crv1, path_middle1)
        right_middle_model2 = rs.ExtrudeCurve(right_middle_crv2, path_middle2)
        right_middle_model3 = rs.ExtrudeCurve(right_middle_crv3, path_middle3)
        right_lower_model = rs.ExtrudeCurve(right_lower_crv, path_lower)

        rs.CapPlanarHoles(right_upper_model)
        rs.CapPlanarHoles(right_middle_model1)
        rs.CapPlanarHoles(right_middle_model2)
        rs.CapPlanarHoles(right_middle_model3)
        rs.CapPlanarHoles(right_lower_model)

        """
        3   Deploy Polysrf.
        """
        trans_upper = (0, 0, layer_t_2 + layer_t_3 + layer_t_4 + layer_t_5)
        rs.MoveObjects([left_upper_model, right_upper_model], trans_upper)

        trans_middle1 = (0, 0, layer_t_3 + layer_t_4 + layer_t_5)
        rs.MoveObjects([left_middle_model1, right_middle_model1], trans_middle1)

        trans_middle2 = (0, 0, layer_t_4 + layer_t_5)
        rs.MoveObjects([left_middle_model2, right_middle_model2], trans_middle2)

        trans_middle3 = (0, 0, layer_t_5)
        rs.MoveObjects([left_middle_model3, right_middle_model3], trans_middle3)


        left_models = [left_upper_model, left_middle_model1, left_middle_model2, left_middle_model3, left_lower_model]
        right_models = [right_upper_model, right_middle_model1, right_middle_model2, right_middle_model3, right_lower_model]

        rs.DeleteObject(path_upper)
        rs.DeleteObject(path_middle1)
        rs.DeleteObject(path_middle2)
        rs.DeleteObject(path_middle3)
        rs.DeleteObject(path_lower)

    else:
        sys.exit()

    return left_models, right_models

# ------------------------------------------------------------------------------
# SHIGUCHI------------------------------------------------------------------------
def make_TOME(dx, dy, KUMIKI_info):
    """Make TOME lists ; upper shape, middle shape, lower shape (3 Layers)
    Receives:
        (dx, dy)        pt      Base point to make KUMIKI

        KUMIKI_info     list    Information of KUMIKI to make
                                [m1_info, m2_info, m1_model, m2_model, direction]
        m1_info         list    list of material1 information
                                [x_m1, y_m1, z_m, m1_points]
        m2_info         list    list of material2 information
                                [x_m2, y_m2, z_m, m2_points]
        m1_points       list    list of material1 points
                                [m1_p0, m1_p1, m1_p2, m1_p3]
        m2_points       list    list of material2 points1
                                [m2_p0, m2_p1, m2_p2, m2_p3]
    Returns:
        m1_lists        list    list of material1 information
        m2_lists        list    list of material2 information

        # m1_crvs         [guid]  material1 crvs ; upper, middle, lower
        # m2_crvs         [guid]  material2 crvs ; upper, middle, lower

        SEN_info        list    list of SEN information

    1   Get Parameters from KUMIKI_info.
    """

    m1_info = KUMIKI_info[0]
    m2_info = KUMIKI_info[1]
    m1_model = KUMIKI_info[2]
    m2_model = KUMIKI_info[3]
    direction = KUMIKI_info[4]

    x_m1 = m1_info[0]
    y_m1 = m1_info[1]

    x_m2 = m2_info[0]
    y_m2 = m2_info[1]

    z_m = m1_info[2]

    m1_points = m1_info[3]
    m2_points = m2_info[3]

    m1_p0 = m1_points[0]
    m1_p1 = m1_points[1]
    m1_p2 = m1_points[2]
    m1_p3 = m1_points[3]

    m2_p0 = m2_points[0]
    m2_p1 = m2_points[1]
    m2_p2 = m2_points[2]
    m2_p3 = m2_points[3]

    """
    2   Get points of TOME.
    """
    x_k = x_m2
    y_k = y_m1

    """
    # NOTE:
    By direction, x_k, y_k change.
    """
    if direction == 'UpperRight':
        y_k = -y_k
    elif direction == 'LowerRight':
        pass
    elif direction == 'UpperLeft':
        y_k = -y_k
    elif direction == 'LowerLeft':
        pass
    else:
        sys.exit()

    p0 = (dx + x_k, dy + y_k)
    p1 = (dx, dy)

    KUMIKI_points = [p0, p1]

    """
    3   Make temporary 3D models.
    """
    # material1
    # WARNING: Have to delete the last element of m1_points
    # Upper
    m1_upper = m1_points[:-1]
    m1_upper.extend(KUMIKI_points)
    m1_upper.append(m1_points[0])

    m1_upper_crv = rs.AddPolyline(m1_upper)

    # Middle
    m1_middle = m1_points[:-1]
    m1_middle.extend(KUMIKI_points)
    m1_middle.append(m1_points[0])

    m1_middle_crv = rs.AddPolyline(m1_middle)

    # Lower
    m1_lower = m1_points[:-1]
    m1_lower.extend(KUMIKI_points)
    m1_lower.append(m1_points[0])

    m1_lower_crv = rs.AddPolyline(m1_lower)

    m1_crvs = [m1_upper_crv, m1_middle_crv, m1_lower_crv]

    # material2
    # WARNING: Have to delete the last element of m2_points

    # Upper
    m2_upper = m2_points[:-1]
    m2_upper.extend(KUMIKI_points)
    m2_upper.append(m2_points[0])

    m2_upper_crv = rs.AddPolyline(m2_upper)

    # Middle
    m2_middle = m2_points[:-1]
    m2_middle.extend(KUMIKI_points)
    m2_middle.append(m2_points[0])

    m2_middle_crv = rs.AddPolyline(m2_middle)

    # Lower
    m2_lower = m2_points[:-1]
    m2_lower.extend(KUMIKI_points)
    m2_lower.append(m2_points[0])

    m2_lower_crv = rs.AddPolyline(m2_lower)

    m2_crvs = [m2_upper_crv, m2_middle_crv, m2_lower_crv]

    t_m1_models, t_m2_models = make_SHIGUCHI_3D(KUMIKI_info, m1_crvs, m2_crvs)
    rs.DeleteObjects(m1_crvs)
    rs.DeleteObjects(m2_crvs)

    """
    3   Get SEN information to make 2D KUMIKI.
    """
    SEN_info = get_SHIGUCHI_SEN_info(dx, dy, KUMIKI_info, x_k)

    # upper shape
    upper_shape_m1, upper_shape_m2 =\
    SHIGUCHI_make_upper_shape_points_list(dx, dy, KUMIKI_info, SEN_info)

    upper_shape_m1_upper_row = upper_shape_m1[0]
    upper_shape_m1_lower_row = upper_shape_m1[1]

    upper_shape_m2_upper_row = upper_shape_m2[0]
    upper_shape_m2_lower_row = upper_shape_m2[1]

    # lower shape
    lower_shape_m1, lower_shape_m2 =\
    SHIGUCHI_make_lower_shape_points_list(dx, dy, KUMIKI_info, SEN_info)

    lower_shape_m1_upper_row = lower_shape_m1[0]
    lower_shape_m1_lower_row = lower_shape_m1[1]

    lower_shape_m2_upper_row = lower_shape_m2[0]
    lower_shape_m2_lower_row = lower_shape_m2[1]

    # middle shape
    middle_shape_m1, middle_shape_m2 =\
    SHIGUCHI_make_middle_shape_points_list(dx, dy, KUMIKI_info, SEN_info)

    middle_shape_m1_upper_row = middle_shape_m1[0]
    middle_shape_m1_lower_row = middle_shape_m1[1]

    middle_shape_m2_upper_row = middle_shape_m2[0]
    middle_shape_m2_lower_row = middle_shape_m2[1]

    """
    4   Make TOME crvs.
        m1_points       list    list of material1 points
                                [m1_p0, m1_p1, m1_p2, m1_p3]
        m2_points       list    list of material2 points
                                [m2_p0, m2_p1, m2_p2, m2_p3]
    """
    # material1-----------------------------------------------------------------
    # Upper
    m1_upper = []
    m1_upper.append(m1_p0)
    m1_upper.append(m1_p1)
    m1_upper.extend(upper_shape_m1_upper_row)

    m1_upper.append(m1_p2)
    m1_upper.extend(KUMIKI_points)
    m1_upper.extend(upper_shape_m1_lower_row)

    m1_upper.append(m1_p0)

    # m1_upper_crv = rs.AddPolyline(m1_upper)

    # Middle
    m1_middle = []
    m1_middle.append(m1_p0)
    m1_middle.append(m1_p1)
    m1_middle.extend(middle_shape_m1_upper_row)

    m1_middle.append(m1_p2)
    m1_middle.extend(KUMIKI_points)
    m1_middle.extend(middle_shape_m1_lower_row)

    m1_middle.append(m1_p0)

    # m1_middle_crv = rs.AddPolyline(m1_middle)

    # Lower
    m1_lower = []
    m1_lower.append(m1_p0)
    m1_lower.append(m1_p1)
    m1_lower.extend(lower_shape_m1_upper_row)

    m1_lower.append(m1_p2)
    m1_lower.extend(KUMIKI_points)
    m1_lower.extend(lower_shape_m1_lower_row)

    m1_lower.append(m1_p0)

    # m1_lower_crv = rs.AddPolyline(m1_lower)

    m1_lists = [m1_upper, m1_middle, m1_lower]

    # m1_crvs = [m1_upper_crv, m1_middle_crv, m1_lower_crv]

    # material2-----------------------------------------------------------------
    # Upper
    m2_upper = []
    m2_upper.append(m2_p0)
    m2_upper.append(m2_p1)
    m2_upper.extend(upper_shape_m2_upper_row)

    m2_upper.append(m2_p2)
    m2_upper.extend(KUMIKI_points)
    m2_upper.extend(upper_shape_m2_lower_row)

    m2_upper.append(m2_p0)

    # m2_upper_crv = rs.AddPolyline(m2_upper)

    # Middle
    m2_middle = []
    m2_middle.append(m2_p0)
    m2_middle.append(m2_p1)
    m2_middle.extend(middle_shape_m2_upper_row)

    m2_middle.append(m2_p2)
    m2_middle.extend(KUMIKI_points)
    m2_middle.extend(middle_shape_m2_lower_row)

    m2_middle.append(m2_p0)

    # m2_middle_crv = rs.AddPolyline(m2_middle)

    # Lower
    m2_lower = []
    m2_lower.append(m2_p0)
    m2_lower.append(m2_p1)
    m2_lower.extend(lower_shape_m2_upper_row)

    m2_lower.append(m2_p2)
    m2_lower.extend(KUMIKI_points)
    m2_lower.extend(lower_shape_m2_lower_row)

    m2_lower.append(m2_p0)

    # m2_lower_crv = rs.AddPolyline(m2_lower)

    m2_lists = [m2_upper, m2_middle, m2_lower]

    # m2_crvs = [m2_upper_crv, m2_middle_crv, m2_lower_crv]

    rs.DeleteObject(m1_model)
    rs.DeleteObject(m2_model)
    rs.DeleteObjects(t_m1_models)
    rs.DeleteObjects(t_m2_models)

    return m1_lists, m2_lists, SEN_info

def make_IRIWA(dx, dy, KUMIKI_info):
    """Make IRIWA lists ; upper shape, middle shape, lower shape (3 Layers)
    Receives:
        (dx, dy)        pt      Base point to make KUMIKI

        KUMIKI_info     list    Information of KUMIKI to make
                                [m1_info, m2_info, m1_model, m2_model, direction]
        m1_info         list    list of material1 information
                                [x_m1, y_m1, z_m, m1_points]
        m2_info         list    list of material2 information
                                [x_m2, y_m2, z_m, m2_points]
        m1_points       list    list of material1 points
                                [m1_p0, m1_p1, m1_p2, m1_p3]
        m2_points       list    list of material2 points
                                [m2_p0, m2_p1, m2_p2, m2_p3]
    Returns:
        m1_lists        list    list of material1 information
        m2_lists        list    list of material2 information

        # m1_crvs         [guid]  material1 crvs ; upper, middle, lower
        # m2_crvs         [guid]  material2 crvs ; upper, middle, lower

        SEN_info        list    list of SEN information

    1   Get Parameters from KUMIKI_info.
    """

    m1_info = KUMIKI_info[0]
    m2_info = KUMIKI_info[1]
    m1_model = KUMIKI_info[2]
    m2_model = KUMIKI_info[3]
    direction = KUMIKI_info[4]

    x_m1 = m1_info[0]
    y_m1 = m1_info[1]

    x_m2 = m2_info[0]
    y_m2 = m2_info[1]

    z_m = m1_info[2]

    m1_points = m1_info[3]
    m2_points = m2_info[3]

    m1_p0 = m1_points[0]
    m1_p1 = m1_points[1]
    m1_p2 = m1_points[2]
    m1_p3 = m1_points[3]

    m2_p0 = m2_points[0]
    m2_p1 = m2_points[1]
    m2_p2 = m2_points[2]
    m2_p3 = m2_points[3]

    """
    2   Get points of IRIWA.
    """
    x_k = x_m2
    y_k = y_m1

    """
    # NOTE:
    By direction, x_k, y_k change.
    """
    if direction == 'UpperRight':
        y_k = -y_k
    elif direction == 'LowerRight':
        pass
    elif direction == 'UpperLeft':
        y_k = -y_k
    elif direction == 'LowerLeft':
        pass
    else:
        sys.exit()

    """
    # NOTE:
    There are 2 KUMIKI_points list.
    """

    p5 = (dx, dy)
    p4 = (dx, dy + y_k / 3)
    p3 = (dx + x_k / 3, dy + y_k / 3)
    p2 = (dx + x_k / 3, dy)
    p1 = (dx + x_k, dy)
    p0 = (dx + x_k, dy + y_k )

    KUMIKI_points1 = [p0, p1, p2, p3, p4, p5]
    KUMIKI_points2 = [p2, p3, p4, p5]

    """
    3   Make temporary 3D models.
    """
    # material1
    # WARNING: Have to delete the last element of m1_points
    # Upper
    m1_upper = m1_points[:-1]
    m1_upper.extend(KUMIKI_points1)
    m1_upper.append(m1_points[0])

    m1_upper_crv = rs.AddPolyline(m1_upper)

    # Middle
    m1_middle = m1_points[:-1]
    m1_middle.extend(KUMIKI_points1)
    m1_middle.append(m1_points[0])

    m1_middle_crv = rs.AddPolyline(m1_middle)

    # Lower
    m1_lower = m1_points[:-1]
    m1_lower.extend(KUMIKI_points1)
    m1_lower.append(m1_points[0])

    m1_lower_crv = rs.AddPolyline(m1_lower)

    m1_crvs = [m1_upper_crv, m1_middle_crv, m1_lower_crv]

    # material2
    # WARNING: Have to delete the last element of m2_points

    # Upper
    m2_upper = m2_points[:-1]
    m2_upper.extend(KUMIKI_points2)
    m2_upper.append(m2_points[0])

    m2_upper_crv = rs.AddPolyline(m2_upper)

    # Middle
    m2_middle = m2_points[:-1]
    m2_middle.extend(KUMIKI_points2)
    m2_middle.append(m2_points[0])

    m2_middle_crv = rs.AddPolyline(m2_middle)

    # Lower
    m2_lower = m2_points[:-1]
    m2_lower.extend(KUMIKI_points2)
    m2_lower.append(m2_points[0])

    m2_lower_crv = rs.AddPolyline(m2_lower)

    m2_crvs = [m2_upper_crv, m2_middle_crv, m2_lower_crv]

    t_m1_models, t_m2_models = make_SHIGUCHI_3D(KUMIKI_info, m1_crvs, m2_crvs)
    rs.DeleteObjects(m1_crvs)
    rs.DeleteObjects(m2_crvs)

    """
    4   Get offset num.
    """
    minimum = 0
    maximum = 0.3

    offset = rs.GetReal("Put the offset num to fit KUMIKI tight. (0.0 < offset < 0.3)",\
                        0.1, minimum, maximum)

    # NOTE: offset num is not parametric number. It's always fixed.

    """
    5   Get points of ARI.
        up to direction
        New KUMIKI points1 -> offset num
            KUMIKI points2 -> ofset num
    """
    # KUMIKI_points1    reflect offset
    p5 = (dx, dy)
    p4 = (dx, dy + y_k / 3)
    p3 = (dx + x_k / 3, dy + y_k / 3)
    p2 = (dx + x_k / 3, dy)
    p1 = (dx + x_k, dy)
    p0 = (dx + x_k, dy + y_k )

    KUMIKI_points1 = [p0, p1, p2, p3, p4, p5]

    if direction == 'UpperRight':
        # KUMIKI_points2
        p5 = (dx, dy)
        p4 = (dx, dy + y_k / 3)
        p3 = (dx + x_k / 3 + offset, dy + y_k / 3)
        p2 = (dx + x_k / 3 + offset, dy)
        p1 = (dx + x_k, dy)
        p0 = (dx + x_k, dy + y_k )

        KUMIKI_points2 = [p2, p3, p4, p5]

    elif direction == 'LowerRight':
        # KUMIKI_points2
        p5 = (dx, dy)
        p4 = (dx, dy + y_k / 3)
        p3 = (dx + x_k / 3 + offset, dy + y_k / 3)
        p2 = (dx + x_k / 3 + offset, dy)
        p1 = (dx + x_k, dy)
        p0 = (dx + x_k, dy + y_k )

        KUMIKI_points2 = [p2, p3, p4, p5]

    elif direction == 'UpperLeft':
        # KUMIKI_points2
        p5 = (dx, dy)
        p4 = (dx, dy + y_k / 3)
        p3 = (dx + x_k / 3 - offset, dy + y_k / 3)
        p2 = (dx + x_k / 3 - offset, dy)
        p1 = (dx + x_k, dy)
        p0 = (dx + x_k, dy + y_k )

        KUMIKI_points2 = [p2, p3, p4, p5]

    elif direction == 'LowerLeft':
        # KUMIKI_points2
        p5 = (dx, dy)
        p4 = (dx, dy + y_k / 3)
        p3 = (dx + x_k / 3 - offset, dy + y_k / 3)
        p2 = (dx + x_k / 3 - offset, dy)
        p1 = (dx + x_k, dy)
        p0 = (dx + x_k, dy + y_k )

        KUMIKI_points2 = [p2, p3, p4, p5]

    else:
        sys.exit()

    """
    6   Get SEN information to make 2D KUMIKI.
    """
    SEN_info = get_SHIGUCHI_SEN_info(dx, dy, KUMIKI_info, x_k)

    # upper shape
    upper_shape_m1, upper_shape_m2 =\
    SHIGUCHI_make_upper_shape_points_list(dx, dy, KUMIKI_info, SEN_info)

    upper_shape_m1_upper_row = upper_shape_m1[0]
    upper_shape_m1_lower_row = upper_shape_m1[1]

    upper_shape_m2_upper_row = upper_shape_m2[0]
    upper_shape_m2_lower_row = upper_shape_m2[1]

    # lower shape
    lower_shape_m1, lower_shape_m2 =\
    SHIGUCHI_make_lower_shape_points_list(dx, dy, KUMIKI_info, SEN_info)

    lower_shape_m1_upper_row = lower_shape_m1[0]
    lower_shape_m1_lower_row = lower_shape_m1[1]

    lower_shape_m2_upper_row = lower_shape_m2[0]
    lower_shape_m2_lower_row = lower_shape_m2[1]

    # middle shape
    middle_shape_m1, middle_shape_m2 =\
    SHIGUCHI_make_middle_shape_points_list(dx, dy, KUMIKI_info, SEN_info)

    middle_shape_m1_upper_row = middle_shape_m1[0]
    middle_shape_m1_lower_row = middle_shape_m1[1]

    middle_shape_m2_upper_row = middle_shape_m2[0]
    middle_shape_m2_lower_row = middle_shape_m2[1]

    """
    7   Make IRIWA lists.
        m1_points       list    list of material1 points
                                [m1_p0, m1_p1, m1_p2, m1_p3]
        m2_points       list    list of material2 points
                                [m2_p0, m2_p1, m2_p2, m2_p3]
    """

    # material1-----------------------------------------------------------------
    # Upper
    m1_upper = []
    m1_upper.append(m1_p0)
    m1_upper.append(m1_p1)
    m1_upper.extend(upper_shape_m1_upper_row)

    m1_upper.append(m1_p2)
    m1_upper.extend(KUMIKI_points1)
    m1_upper.extend(upper_shape_m1_lower_row)

    m1_upper.append(m1_p0)

    # m1_upper_crv = rs.AddPolyline(m1_upper)

    # Middle
    m1_middle = []
    m1_middle.append(m1_p0)
    m1_middle.append(m1_p1)
    m1_middle.extend(middle_shape_m1_upper_row)

    m1_middle.append(m1_p2)
    m1_middle.extend(KUMIKI_points1)
    m1_middle.extend(middle_shape_m1_lower_row)

    m1_middle.append(m1_p0)

    # m1_middle_crv = rs.AddPolyline(m1_middle)

    # Lower
    m1_lower = []
    m1_lower.append(m1_p0)
    m1_lower.append(m1_p1)
    m1_lower.extend(lower_shape_m1_upper_row)

    m1_lower.append(m1_p2)
    m1_lower.extend(KUMIKI_points1)
    m1_lower.extend(lower_shape_m1_lower_row)

    m1_lower.append(m1_p0)

    # m1_lower_crv = rs.AddPolyline(m1_lower)

    m1_lists = [m1_upper, m1_middle, m1_lower]

    # m1_crvs = [m1_upper_crv, m1_middle_crv, m1_lower_crv]

    # material2-----------------------------------------------------------------
    # Upper
    m2_upper = []
    m2_upper.append(m2_p0)
    m2_upper.append(m2_p1)
    m2_upper.extend(upper_shape_m2_upper_row)

    m2_upper.append(m2_p2)
    m2_upper.extend(KUMIKI_points2)
    m2_upper.extend(upper_shape_m2_lower_row)

    m2_upper.append(m2_p0)

    # m2_upper_crv = rs.AddPolyline(m2_upper)

    # Middle
    m2_middle = []
    m2_middle.append(m2_p0)
    m2_middle.append(m2_p1)
    m2_middle.extend(middle_shape_m2_upper_row)

    m2_middle.append(m2_p2)
    m2_middle.extend(KUMIKI_points2)
    m2_middle.extend(middle_shape_m2_lower_row)

    m2_middle.append(m2_p0)

    # m2_middle_crv = rs.AddPolyline(m2_middle)

    # Lower
    m2_lower = []
    m2_lower.append(m2_p0)
    m2_lower.append(m2_p1)
    m2_lower.extend(lower_shape_m2_upper_row)

    m2_lower.append(m2_p2)
    m2_lower.extend(KUMIKI_points2)
    m2_lower.extend(lower_shape_m2_lower_row)

    m2_lower.append(m2_p0)

    # m2_lower_crv = rs.AddPolyline(m2_lower)

    m2_lists = [m2_upper, m2_middle, m2_lower]

    # m2_crvs = [m2_upper_crv, m2_middle_crv, m2_lower_crv]

    rs.DeleteObject(m1_model)
    rs.DeleteObject(m2_model)
    rs.DeleteObjects(t_m1_models)
    rs.DeleteObjects(t_m2_models)

    return m1_lists, m2_lists, SEN_info

def make_SANMAIKUMI(dx, dy, KUMIKI_info):
    """Make SANMAIKUMI lists ; upper shape, middle shape, lower shape (3 Layers)
    Receives:
        (dx, dy)        pt      Base point to make KUMIKI

        KUMIKI_info     list    Information of KUMIKI to make
                                [m1_info, m2_info, m1_model, m2_model, direction]
        m1_info         list    list of material1 information
                                [x_m1, y_m1, z_m, m1_points]
        m2_info         list    list of material2 information
                                [x_m2, y_m2, z_m, m2_points]
        m1_points       list    list of material1 points
                                [m1_p0, m1_p1, m1_p2, m1_p3]
        m2_points       list    list of material2 points
                                [m2_p0, m2_p1, m2_p2, m2_p3]
    Returns:
        m1_lists        list    list of material1 information
        m2_lists        list    list of material2 information

        # m1_crvs         [guid]  material1 crvs ; upper, middle, lower
        # m2_crvs         [guid]  material2 crvs ; upper, middle, lower

        SEN_info        list    list of SEN information

    1   Get Parameters from KUMIKI_info.
    """

    m1_info = KUMIKI_info[0]
    m2_info = KUMIKI_info[1]
    m1_model = KUMIKI_info[2]
    m2_model = KUMIKI_info[3]
    direction = KUMIKI_info[4]

    x_m1 = m1_info[0]
    y_m1 = m1_info[1]

    x_m2 = m2_info[0]
    y_m2 = m2_info[1]

    z_m = m1_info[2]

    m1_points = m1_info[3]
    m2_points = m2_info[3]

    m1_p0 = m1_points[0]
    m1_p1 = m1_points[1]
    m1_p2 = m1_points[2]
    m1_p3 = m1_points[3]

    m2_p0 = m2_points[0]
    m2_p1 = m2_points[1]
    m2_p2 = m2_points[2]
    m2_p3 = m2_points[3]

    """
    2   Get points of SANMAIKUMI.
    """
    x_k = x_m2
    y_k = y_m1

    """
    # NOTE:
    By direction, x_k, y_k change.
    """
    if direction == 'UpperRight':
        y_k = -y_k
    elif direction == 'LowerRight':
        pass
    elif direction == 'UpperLeft':
        y_k = -y_k
    elif direction == 'LowerLeft':
        pass
    else:
        sys.exit()

    m1_p0 = m1_points[0]
    m1_p1 = m1_points[1]
    m1_p2 = m1_points[2]

    m2_p0 = m2_points[0]
    m2_p1 = m2_points[1]
    m2_p2 = m2_points[2]

    p1 = (dx, dy)
    p0 = (dx + x_k, dy + y_k)

    KUMIKI_points1 = [p0, m2_p2, p1]
    KUMIKI_points2 = [p0, m1_p2, p1]

    """
    3   Make temporary 3D models.
    """
    # material1
    # WARNING: Have to delete the last element of m1_points
    # Upper
    m1_upper = m1_points[:-1]
    m1_upper.extend(KUMIKI_points1)
    m1_upper.append(m1_points[0])

    m1_upper_crv = rs.AddPolyline(m1_upper)

    # Lower
    m1_lower = m1_points[:-1]
    m1_lower.extend(KUMIKI_points1)
    m1_lower.append(m1_points[0])

    m1_lower_crv = rs.AddPolyline(m1_lower)

    # Middle
    m1_points.append(m1_p0)

    m1_middle_crv = rs.AddPolyline(m1_points)

    m1_crvs = [m1_upper_crv, m1_middle_crv, m1_lower_crv]


    # material2
    # WARNING: Have to delete the last element of m2_points

    # Middle
    m2_middle = m2_points[:-1]
    m2_middle.extend(KUMIKI_points2)
    m2_middle.append(m2_points[0])

    m2_middle_crv = rs.AddPolyline(m2_middle)

    # Upper & Lower
    m2_points.append(m2_p0)

    m2_upper_crv = rs.AddPolyline(m2_points)
    m2_lower_crv = rs.AddPolyline(m2_points)

    m2_crvs = [m2_upper_crv, m2_middle_crv, m2_lower_crv]

    t_m1_models, t_m2_models = make_SHIGUCHI_3D(KUMIKI_info, m1_crvs, m2_crvs)
    rs.DeleteObjects(m1_crvs)
    rs.DeleteObjects(m2_crvs)

    """
    4   Get SEN information to make 2D KUMIKI.
    """
    SEN_info = get_SHIGUCHI_SEN_info(dx, dy, KUMIKI_info, x_k)

    # upper shape
    upper_shape_m1, upper_shape_m2 =\
    SHIGUCHI_make_upper_shape_points_list(dx, dy, KUMIKI_info, SEN_info)

    upper_shape_m1_upper_row = upper_shape_m1[0]
    upper_shape_m1_lower_row = upper_shape_m1[1]

    upper_shape_m2_upper_row = upper_shape_m2[0]
    upper_shape_m2_lower_row = upper_shape_m2[1]

    # lower shape
    lower_shape_m1, lower_shape_m2 =\
    SHIGUCHI_make_lower_shape_points_list(dx, dy, KUMIKI_info, SEN_info)

    lower_shape_m1_upper_row = lower_shape_m1[0]
    lower_shape_m1_lower_row = lower_shape_m1[1]

    lower_shape_m2_upper_row = lower_shape_m2[0]
    lower_shape_m2_lower_row = lower_shape_m2[1]

    # middle shape
    middle_shape_m1, middle_shape_m2 =\
    SHIGUCHI_make_middle_shape_points_list(dx, dy, KUMIKI_info, SEN_info)

    middle_shape_m1_upper_row = middle_shape_m1[0]
    middle_shape_m1_lower_row = middle_shape_m1[1]

    middle_shape_m2_upper_row = middle_shape_m2[0]
    middle_shape_m2_lower_row = middle_shape_m2[1]

    """
    5   Make SANMAIKUMI lists.
        m1_points       list    list of material1 points
                                [m1_p0, m1_p1, m1_p2, m1_p3]
        m2_points       list    list of material2 points
                                [m2_p0, m2_p1, m2_p2, m2_p3]
    """
    # material1-----------------------------------------------------------------
    # Upper
    m1_upper = []
    m1_upper.append(m1_p0)
    m1_upper.append(m1_p1)
    m1_upper.extend(upper_shape_m1_upper_row)

    m1_upper.append(m1_p2)
    m1_upper.extend(KUMIKI_points1)
    m1_upper.extend(upper_shape_m1_lower_row)

    m1_upper.append(m1_p0)

    # m1_upper_crv = rs.AddPolyline(m1_upper)

    # Lower
    m1_lower = []
    m1_lower.append(m1_p0)
    m1_lower.append(m1_p1)
    m1_lower.extend(lower_shape_m1_upper_row)

    m1_lower.append(m1_p2)
    m1_lower.extend(KUMIKI_points1)
    m1_lower.extend(lower_shape_m1_lower_row)

    m1_lower.append(m1_p0)

    # m1_lower_crv = rs.AddPolyline(m1_lower)

    # Middle
    m1_middle = []
    m1_middle.append(m1_p0)
    m1_middle.append(m1_p1)
    m1_middle.extend(middle_shape_m1_upper_row)

    m1_middle.append(m1_p2)
    m1_middle.append(m1_p3)
    m1_middle.extend(middle_shape_m1_lower_row)

    m1_middle.append(m1_p0)

    # m1_middle_crv = rs.AddPolyline(m1_middle)

    m1_lists = [m1_upper, m1_middle, m1_lower]

    # m1_crvs = [m1_upper_crv, m1_middle_crv, m1_lower_crv]

    # material2-----------------------------------------------------------------
    # Middle
    m2_middle = []
    m2_middle.append(m2_p0)
    m2_middle.append(m2_p1)
    m2_middle.extend(middle_shape_m2_upper_row)

    m2_middle.append(m2_p2)
    m2_middle.extend(KUMIKI_points2)
    m2_middle.extend(middle_shape_m2_lower_row)

    m2_middle.append(m2_p0)

    # m2_middle_crv = rs.AddPolyline(m2_middle)

    # Upper
    m2_upper = []
    m2_upper.append(m2_p0)
    m2_upper.append(m2_p1)
    m2_upper.extend(upper_shape_m2_upper_row)

    m2_upper.append(m2_p2)
    m2_upper.append(m2_p3)
    m2_upper.extend(upper_shape_m2_lower_row)

    m2_upper.append(m2_p0)

    # m2_upper_crv = rs.AddPolyline(m2_upper)

    # Lower
    m2_lower = []
    m2_lower.append(m2_p0)
    m2_lower.append(m2_p1)
    m2_lower.extend(upper_shape_m2_upper_row)

    m2_lower.append(m2_p2)
    m2_lower.append(m2_p3)
    m2_lower.extend(upper_shape_m2_lower_row)

    m2_lower.append(m2_p0)

    # m2_lower_crv = rs.AddPolyline(m2_lower)

    m2_lists = [m2_upper, m2_middle, m2_lower]

    # m2_crvs = [m2_upper_crv, m2_middle_crv, m2_lower_crv]

    rs.DeleteObject(m1_model)
    rs.DeleteObject(m2_model)
    rs.DeleteObjects(t_m1_models)
    rs.DeleteObjects(t_m2_models)

    return m1_lists, m2_lists, SEN_info

def make_AIKAKI_KUMITE(dx, dy, KUMIKI_info):
    """Make AIKAKI lists ; upper shape, middle shape, lower shape (3 Layers)
    Receives:
        (dx, dy)        pt      Base point to make KUMIKI

        KUMIKI_info     list    Information of KUMIKI to make
                                [m1_info, m2_info, m1_model, m2_model, direction]
        m1_info         list    list of material1 information
                                [x_m1, y_m1, z_m, m1_points]
        m2_info         list    list of material2 information
                                [x_m2, y_m2, z_m, m2_points]
        m1_points       list    list of material1 points
                                [m1_p0, m1_p1, m1_p2, m1_p3]
        m2_points       list    list of material2 points
                                [m2_p0, m2_p1, m2_p2, m2_p3]
    Returns:
        m1_lists        list    list of material1 information
        m2_lists        list    list of material2 information

        # m1_crvs         [guid]  material1 crvs ; upper, middle, lower
        # m2_crvs         [guid]  material2 crvs ; upper, middle, lower

        SEN_info        list    list of SEN information

    1   Get Parameters from KUMIKI_info.
    """

    m1_info = KUMIKI_info[0]
    m2_info = KUMIKI_info[1]
    m1_model = KUMIKI_info[2]
    m2_model = KUMIKI_info[3]
    direction = KUMIKI_info[4]

    x_m1 = m1_info[0]
    y_m1 = m1_info[1]

    x_m2 = m2_info[0]
    y_m2 = m2_info[1]

    z_m = m1_info[2]

    m1_points = m1_info[3]
    m2_points = m2_info[3]

    m1_p0 = m1_points[0]
    m1_p1 = m1_points[1]
    m1_p2 = m1_points[2]
    m1_p3 = m1_points[3]

    m2_p0 = m2_points[0]
    m2_p1 = m2_points[1]
    m2_p2 = m2_points[2]
    m2_p3 = m2_points[3]

    """
    2   Get points of AIKAKI.
    """
    x_k = x_m2
    y_k = y_m1

    """
    # NOTE:
    By direction, x_k, y_k change.
    """
    if direction == 'UpperRight':
        y_k = -y_k
    elif direction == 'LowerRight':
        pass
    elif direction == 'UpperLeft':
        y_k = -y_k
    elif direction == 'LowerLeft':
        pass
    else:
        sys.exit()

    m1_p0 = m1_points[0]
    m1_p1 = m1_points[1]
    m1_p2 = m1_points[2]

    m2_p0 = m2_points[0]
    m2_p1 = m2_points[1]
    m2_p2 = m2_points[2]

    p1 = (dx, dy)
    p0 = (dx + x_k, dy + y_k)

    KUMIKI_points1 = [p0, m2_p2, p1]
    KUMIKI_points2 = [p0, m1_p2, p1]

    """
    3   Make temporary 3D models.
    """
    # material1
    # WARNING: Have to delete the last element of m1_points
    # Middle
    m1_middle = m1_points[:-1]
    m1_middle.extend(KUMIKI_points1)
    m1_middle.append(m1_points[0])

    m1_middle_crv = rs.AddPolyline(m1_middle)

    # Lower
    m1_lower = m1_points[:-1]
    m1_lower.extend(KUMIKI_points1)
    m1_lower.append(m1_points[0])

    m1_lower_crv = rs.AddPolyline(m1_lower)

    # Upper
    m1_points.append(m1_p0)

    m1_upper_crv = rs.AddPolyline(m1_points)

    m1_crvs = [m1_upper_crv, m1_middle_crv, m1_lower_crv]


    # material2
    # WARNING: Have to delete the last element of m2_points

    # Upper
    m2_upper = m2_points[:-1]
    m2_upper.extend(KUMIKI_points2)
    m2_upper.append(m2_points[0])

    m2_upper_crv = rs.AddPolyline(m2_upper)

    # middle & Lower
    m2_points.append(m2_p0)

    m2_middle_crv = rs.AddPolyline(m2_points)
    m2_lower_crv = rs.AddPolyline(m2_points)

    m2_crvs = [m2_upper_crv, m2_middle_crv, m2_lower_crv]

    t_m1_models, t_m2_models = make_SHIGUCHI_3D(KUMIKI_info, m1_crvs, m2_crvs)
    rs.DeleteObjects(m1_crvs)
    rs.DeleteObjects(m2_crvs)

    """
    4   Get SEN information to make 2D KUMIKI.
    """
    SEN_info = get_SHIGUCHI_SEN_info(dx, dy, KUMIKI_info, x_k)

    # upper shape
    upper_shape_m1, upper_shape_m2 =\
    SHIGUCHI_make_upper_shape_points_list(dx, dy, KUMIKI_info, SEN_info)

    upper_shape_m1_upper_row = upper_shape_m1[0]
    upper_shape_m1_lower_row = upper_shape_m1[1]

    upper_shape_m2_upper_row = upper_shape_m2[0]
    upper_shape_m2_lower_row = upper_shape_m2[1]

    # lower shape
    lower_shape_m1, lower_shape_m2 =\
    SHIGUCHI_make_lower_shape_points_list(dx, dy, KUMIKI_info, SEN_info)

    lower_shape_m1_upper_row = lower_shape_m1[0]
    lower_shape_m1_lower_row = lower_shape_m1[1]

    lower_shape_m2_upper_row = lower_shape_m2[0]
    lower_shape_m2_lower_row = lower_shape_m2[1]

    # middle shape
    middle_shape_m1, middle_shape_m2 =\
    SHIGUCHI_make_middle_shape_points_list(dx, dy, KUMIKI_info, SEN_info)

    middle_shape_m1_upper_row = middle_shape_m1[0]
    middle_shape_m1_lower_row = middle_shape_m1[1]

    middle_shape_m2_upper_row = middle_shape_m2[0]
    middle_shape_m2_lower_row = middle_shape_m2[1]

    """
    5   Make AIKAKI lists.
        m1_points       list    list of material1 points
                                [m1_p0, m1_p1, m1_p2, m1_p3]
        m2_points       list    list of material2 points
                                [m2_p0, m2_p1, m2_p2, m2_p3]
    """
    # Upper
    m1_upper = []
    m1_upper.append(m1_p0)
    m1_upper.append(m1_p1)
    m1_upper.extend(upper_shape_m1_upper_row)

    m1_upper.append(m1_p2)
    m1_upper.append(m1_p3)
    m1_upper.extend(upper_shape_m1_lower_row)

    m1_upper.append(m1_p0)

    # m1_upper_crv = rs.AddPolyline(m1_upper)

    # Middle
    m1_middle = []
    m1_middle.append(m1_p0)
    m1_middle.append(m1_p1)
    m1_middle.extend(middle_shape_m1_upper_row)

    m1_middle.append(m1_p2)
    m1_middle.extend(KUMIKI_points1)
    m1_middle.extend(middle_shape_m1_lower_row)

    m1_middle.append(m1_p0)

    # m1_middle_crv = rs.AddPolyline(m1_middle)

    # Lower
    m1_lower = []
    m1_lower.append(m1_p0)
    m1_lower.append(m1_p1)
    m1_lower.extend(lower_shape_m1_upper_row)

    m1_lower.append(m1_p2)
    m1_lower.extend(KUMIKI_points1)
    m1_lower.extend(lower_shape_m1_lower_row)

    m1_lower.append(m1_p0)

    # m1_lower_crv = rs.AddPolyline(m1_lower)

    m1_lists = [m1_upper, m1_middle, m1_lower]

    # m1_crvs = [m1_upper_crv, m1_middle_crv, m1_lower_crv]

    # material2-----------------------------------------------------------------
    # Upper
    m2_upper = []
    m2_upper.append(m2_p0)
    m2_upper.append(m2_p1)
    m2_upper.extend(upper_shape_m2_upper_row)

    m2_upper.append(m2_p2)
    m2_upper.extend(KUMIKI_points2)
    m2_upper.extend(upper_shape_m2_lower_row)

    m2_upper.append(m2_p0)

    # m2_upper_crv = rs.AddPolyline(m2_upper)

    # Middle
    m2_middle = []
    m2_middle.append(m2_p0)
    m2_middle.append(m2_p1)
    m2_middle.extend(middle_shape_m2_upper_row)

    m2_middle.append(m2_p2)
    m2_middle.append(m2_p3)
    m2_middle.extend(middle_shape_m2_lower_row)

    m2_middle.append(m2_p0)

    # m2_middle_crv = rs.AddPolyline(m2_middle)

    # Lower
    m2_lower = []
    m2_lower.append(m2_p0)
    m2_lower.append(m2_p1)
    m2_lower.extend(lower_shape_m2_upper_row)

    m2_lower.append(m2_p2)
    m2_lower.append(m2_p3)
    m2_lower.extend(lower_shape_m2_lower_row)

    m2_lower.append(m2_p0)

    # m2_lower_crv = rs.AddPolyline(m2_lower)

    m2_lists = [m2_upper, m2_middle, m2_lower]

    # m2_crvs = [m2_upper_crv, m2_middle_crv, m2_lower_crv]

    rs.DeleteObject(m1_model)
    rs.DeleteObject(m2_model)
    rs.DeleteObjects(t_m1_models)
    rs.DeleteObjects(t_m2_models)

    return m1_lists, m2_lists, SEN_info

def make_HAKO_KUMITE(dx, dy, KUMIKI_info):
    """Make HAKO lists ; upper shape, middle shape, lower shape (3 Layers)
    Receives:
        (dx, dy)        pt      Base point to make KUMIKI

        KUMIKI_info     list    Information of KUMIKI to make
                                [m1_info, m2_info, m1_model, m2_model, direction]
        m1_info         list    list of material1 information
                                [x_m1, y_m1, z_m, m1_points]
        m2_info         list    list of material2 information
                                [x_m2, y_m2, z_m, m2_points]
        m1_points       list    list of material1 points
                                [m1_p0, m1_p1, m1_p2, m1_p3]
        m2_points       list    list of material2 points
                                [m2_p0, m2_p1, m2_p2, m2_p3]
    Returns:
        m1_lists        list    list of material1 information
        m2_lists        list    list of material2 information

        # m1_crvs         [guid]  material1 crvs ; upper, middle, lower
        # m2_crvs         [guid]  material2 crvs ; upper, middle, lower

        SEN_info        list    list of SEN information

    1   Get Parameters from KUMIKI_info.
    """

    m1_info = KUMIKI_info[0]
    m2_info = KUMIKI_info[1]
    m1_model = KUMIKI_info[2]
    m2_model = KUMIKI_info[3]
    direction = KUMIKI_info[4]

    x_m1 = m1_info[0]
    y_m1 = m1_info[1]

    x_m2 = m2_info[0]
    y_m2 = m2_info[1]

    z_m = m1_info[2]

    m1_points = m1_info[3]
    m2_points = m2_info[3]

    m1_p0 = m1_points[0]
    m1_p1 = m1_points[1]
    m1_p2 = m1_points[2]
    m1_p3 = m1_points[3]

    m2_p0 = m2_points[0]
    m2_p1 = m2_points[1]
    m2_p2 = m2_points[2]
    m2_p3 = m2_points[3]

    """
    2   Get points of HAKO.
    """
    x_k = x_m2
    y_k = y_m1

    """
    # NOTE:
    By direction, x_k, y_k change.
    """
    if direction == 'UpperRight':
        y_k = -y_k
    elif direction == 'LowerRight':
        pass
    elif direction == 'UpperLeft':
        y_k = -y_k
    elif direction == 'LowerLeft':
        pass
    else:
        sys.exit()

    """
    # NOTE:
    There are 2 KUMIKI_points list.
    """
    m1_p0 = m1_points[0]
    m1_p1 = m1_points[1]
    m1_p2 = m1_points[2]

    m2_p0 = m2_points[0]
    m2_p1 = m2_points[1]
    m2_p2 = m2_points[2]

    p4 = (dx, dy)
    p3 = (dx + x_k / 3, dy)
    p2 = (dx + x_k / 3, dy + 2 * y_k / 3)
    p1 = (dx + x_k, dy + 2 * y_k / 3)
    p0 = (dx + x_k, dy + y_k)

    KUMIKI_points1 = [p0, p1, p2, p3, p4]
    KUMIKI_points2 = [p0, m1_p2, p4]
    KUMIKI_points3 = [p1, p2, p3, p4]

    """
    3   Make temporary 3D models.
    """
    # material1
    # WARNING: Have to delete the last element of m1_points
    # Upper
    m1_upper = m1_points[:-1]
    m1_upper.extend(KUMIKI_points1)
    m1_upper.append(m1_points[0])

    m1_upper_crv = rs.AddPolyline(m1_upper)

    # Middle
    m1_middle = m1_points[:-1]
    m1_middle.extend(KUMIKI_points1)
    m1_middle.append(m1_points[0])

    m1_middle_crv = rs.AddPolyline(m1_middle)

    # Lower
    m1_lower = m1_points[:-1]
    m1_lower.extend(KUMIKI_points1)
    m1_lower.append(m1_points[0])

    m1_lower_crv = rs.AddPolyline(m1_lower)

    m1_crvs = [m1_upper_crv, m1_middle_crv, m1_lower_crv]

    # material2
    # WARNING: Have to delete the last element of m2_points

    # Upper
    m2_upper = m2_points[:-1]
    m2_upper.extend(KUMIKI_points2)
    m2_upper.append(m2_points[0])

    m2_upper_crv = rs.AddPolyline(m2_upper)

    # Middle
    m2_middle = m2_points[:-1]
    m2_middle.extend(KUMIKI_points2)
    m2_middle.append(m2_points[0])

    m2_middle_crv = rs.AddPolyline(m2_middle)

    # Lower
    m2_lower = m2_points[:-1]
    m2_lower.extend(KUMIKI_points2)
    m2_lower.append(m2_points[0])

    m2_lower_crv = rs.AddPolyline(m2_lower)

    m2_crvs = [m2_upper_crv, m2_middle_crv, m2_lower_crv]

    t_m1_models, t_m2_models = make_SHIGUCHI_3D(KUMIKI_info, m1_crvs, m2_crvs)
    rs.DeleteObjects(m1_crvs)
    rs.DeleteObjects(m2_crvs)

    """
    4   Get SEN information to make 2D KUMIKI.
    """
    SEN_info = get_SHIGUCHI_SEN_info(dx, dy, KUMIKI_info, x_k)

    # upper shape
    upper_shape_m1, upper_shape_m2 =\
    SHIGUCHI_make_upper_shape_points_list(dx, dy, KUMIKI_info, SEN_info)

    upper_shape_m1_upper_row = upper_shape_m1[0]
    upper_shape_m1_lower_row = upper_shape_m1[1]

    upper_shape_m2_upper_row = upper_shape_m2[0]
    upper_shape_m2_lower_row = upper_shape_m2[1]

    # lower shape
    lower_shape_m1, lower_shape_m2 =\
    SHIGUCHI_make_lower_shape_points_list(dx, dy, KUMIKI_info, SEN_info)

    lower_shape_m1_upper_row = lower_shape_m1[0]
    lower_shape_m1_lower_row = lower_shape_m1[1]

    lower_shape_m2_upper_row = lower_shape_m2[0]
    lower_shape_m2_lower_row = lower_shape_m2[1]

    # middle shape
    middle_shape_m1, middle_shape_m2 =\
    SHIGUCHI_make_middle_shape_points_list(dx, dy, KUMIKI_info, SEN_info)

    middle_shape_m1_upper_row = middle_shape_m1[0]
    middle_shape_m1_lower_row = middle_shape_m1[1]

    middle_shape_m2_upper_row = middle_shape_m2[0]
    middle_shape_m2_lower_row = middle_shape_m2[1]

    """
    5   Make HAKO lists.
        m1_points       list    list of material1 points
                                [m1_p0, m1_p1, m1_p2, m1_p3]
        m2_points       list    list of material2 points
                                [m2_p0, m2_p1, m2_p2, m2_p3]
    """
    # material1-----------------------------------------------------------------
    # Upper
    m1_upper = []
    m1_upper.append(m1_p0)
    m1_upper.append(m1_p1)
    m1_upper.extend(upper_shape_m1_upper_row)

    m1_upper.append(m1_p2)
    m1_upper.extend(KUMIKI_points1)
    m1_upper.extend(upper_shape_m1_lower_row)

    m1_upper.append(m1_p0)

    # m1_upper_crv = rs.AddPolyline(m1_upper)

    # Middle
    m1_middle = []
    m1_middle.append(m1_p0)
    m1_middle.append(m1_p1)
    m1_middle.extend(middle_shape_m1_upper_row)

    m1_middle.append(m1_p2)
    m1_middle.extend(KUMIKI_points1)
    m1_middle.extend(middle_shape_m1_lower_row)

    m1_middle.append(m1_p0)

    # m1_middle_crv = rs.AddPolyline(m1_middle)

    # Lower
    m1_lower = []
    m1_lower.append(m1_p0)
    m1_lower.append(m1_p1)
    m1_lower.extend(lower_shape_m1_upper_row)

    m1_lower.append(m1_p2)
    m1_lower.append(m1_p3)
    m1_lower.extend(lower_shape_m1_lower_row)

    m1_lower.append(m1_p0)

    # m1_lower_crv = rs.AddPolyline(m1_lower)

    m1_lists = [m1_upper, m1_middle, m1_lower]

    # m1_crvs = [m1_upper_crv, m1_middle_crv, m1_lower_crv]

    # material2-----------------------------------------------------------------
    # Upper
    m2_upper = []
    m2_upper.append(m2_p0)
    m2_upper.append(m2_p1)
    m2_upper.extend(upper_shape_m2_upper_row)

    m2_upper.append(m2_p2)
    m2_upper.extend(KUMIKI_points3)
    m2_upper.extend(upper_shape_m2_lower_row)

    m2_upper.append(m2_p0)

    # m2_upper_crv = rs.AddPolyline(m2_upper)

    # Middle
    m2_middle = []
    m2_middle.append(m2_p0)
    m2_middle.append(m2_p1)
    m2_middle.extend(middle_shape_m2_upper_row)

    m2_middle.append(m2_p2)
    m2_middle.extend(KUMIKI_points3)
    m2_middle.extend(middle_shape_m2_lower_row)

    m2_middle.append(m2_p0)

    # m2_middle_crv = rs.AddPolyline(m2_middle)

    # Lower
    m2_lower = []
    m2_lower.append(m2_p0)
    m2_lower.append(m2_p1)
    m2_lower.extend(lower_shape_m2_upper_row)

    m2_lower.append(m2_p2)
    m2_lower.extend(KUMIKI_points2)
    m2_lower.extend(lower_shape_m2_lower_row)

    m2_lower.append(m2_p0)

    # m2_lower_crv = rs.AddPolyline(m2_lower)

    m2_lists = [m2_upper, m2_middle, m2_lower]

    # m2_crvs = [m2_upper_crv, m2_middle_crv, m2_lower_crv]

    rs.DeleteObject(m1_model)
    rs.DeleteObject(m2_model)
    rs.DeleteObjects(t_m1_models)
    rs.DeleteObjects(t_m2_models)

    return m1_lists, m2_lists, SEN_info

# SHIGUCHI 3D modeller------------------------------------------------------------
def make_SHIGUCHI_3D(KUMIKI_info, m1_crvs, m2_crvs):
    """Make SHIGUCHI 3D model to show user what it is like.
    Receives:
        KUMIKI_info     list    Information of KUMIKI to make
                                [m1_info, m2_info, m1_model, m2_model, direction]
        m1_info         list    list of material1 information
                                [x_m1, y_m1, z_m, m1_points]
        m2_info         list    list of material2 information
                                [x_m2, y_m2, z_m, m2_points]

        m1_crvs         [guid]  material1 crvs ; upper, middle, lower
                                [m1_upper_crv, m1_middle_crv, m1_lower_crv]
        m2_crvs         [guid]  material2 crvs ; upper, middle, lower
                                [m2_upper_crv, m2_middle_crv, m2_lower_crv]
    Returns:
        m1_models       [guid]  material1 side models (Polysrf) ; upper, middle, lower
                                [m1_upper_model, m1_middle_model, m1_lower_model]
        m2_models       [guid]  material2 side models (Polysrf) ; upper, middle, lower
                                [m2_upper_model, m2_middle_model, m2_lower_model]

    1   Get parameter and objects from list.
    """
    m1_info = KUMIKI_info[0]
    m2_info = KUMIKI_info[1]
    direction = KUMIKI_info[4]

    x_m1 = m1_info[0]
    y_m1 = m1_info[1]

    x_m2 = m2_info[0]
    y_m2 = m2_info[1]

    z_m = m1_info[2]

    m1_points = m1_info[3]
    m2_points = m2_info[3]

    m1_upper_crv = m1_crvs[0]
    m1_middle_crv = m1_crvs[1]
    m1_lower_crv = m1_crvs[2]

    m2_upper_crv = m2_crvs[0]
    m2_middle_crv = m2_crvs[1]
    m2_lower_crv = m2_crvs[2]

    """
    2   Extrude Crvs.
        the z length (thickness) for each layer is 'z_m / 3'
    """
    each_z_m = z_m / 3

    start = (0, 0, 0)
    end = (0, 0, each_z_m)
    path = rs.AddLine(start, end)

    # Leftside
    m1_upper_model = rs.ExtrudeCurve(m1_upper_crv, path)
    m1_middle_model = rs.ExtrudeCurve(m1_middle_crv, path)
    m1_lower_model = rs.ExtrudeCurve(m1_lower_crv, path)

    rs.CapPlanarHoles(m1_upper_model)
    rs.CapPlanarHoles(m1_middle_model)
    rs.CapPlanarHoles(m1_lower_model)

    # Rightside
    m2_upper_model = rs.ExtrudeCurve(m2_upper_crv, path)
    m2_middle_model = rs.ExtrudeCurve(m2_middle_crv, path)
    m2_lower_model = rs.ExtrudeCurve(m2_lower_crv, path)

    rs.CapPlanarHoles(m2_upper_model)
    rs.CapPlanarHoles(m2_middle_model)
    rs.CapPlanarHoles(m2_lower_model)

    """
    3   Deploy Polysrf.
        trans_upper = (0, 0, 2 * each_z_m)
        trans_middle = (0, 0, each_z_m)
    """
    trans_upper = (0, 0, 2 * each_z_m)
    rs.MoveObjects([m1_upper_model, m2_upper_model], trans_upper)

    trans_middle = (0, 0, each_z_m)
    rs.MoveObjects([m1_middle_model, m2_middle_model], trans_middle)


    m1_models = [m1_upper_model, m1_middle_model, m1_lower_model]
    m2_models = [m2_upper_model, m2_middle_model, m2_lower_model]

    rs.DeleteObject(path)

    return m1_models, m2_models

# ------------------------------------------------------------------------------
# SEN FUNCTIONs-----------------------------------------------------------------
def get_TSUGITE_SEN_info(dx, dy, KUMIKI_info, x_k):
    """Gets information of TSUGITE SEN.
    Receives:
        (dx, dy)        pt      Base point to make KUMIKI
        x_k             int     x length of KUMIKI

        KUMIKI_info     list    list of information
                                [m_info, m_model]
        m_info                  [x_m, y_m, z_m, m_points, layer_t]
        m_points                [l_mp0, l_mp1, r_mp0, r_mp1]

        x_m             int     x length of material
        y_m             int     y length of material
        z_m             int     z length of material

    Returns:
        SEN_info        list    list of SEN information
                                [w_sen, n_w_sen, h_sen, t_sen,
                                 l_n, r_n, set, l_offset, r_offset]

        w_sen           int     width of sen
        n_w_sen         int     narrow part width of sen
        h_sen           int     height of sen
        t_sen           int     thickness of sen

        l_n             int     the number of sen on x side of material
        r_n             int     the number of sen on x side of material
        set             int     the number of setback from edge line of material to line up SEN
        l_offset        int     the number of offst between each SENs
        r_offset        int     the number of offst between each SENs

    1   Get parameters from KUMIKI_info
    """
    m_info = KUMIKI_info[0]

    x_m = m_info[0]
    y_m = m_info[1]
    z_m = m_info[2]

    m_points = m_info[3]
    l_mp0 = m_points[0]
    l_mp1 = m_points[1]

    r_mp0 = m_points[2]
    r_mp1 = m_points[3]

    b_p = (dx, dy)

    l_distance = rs.Distance(l_mp0, b_p)
    r_distance = rs.Distance(r_mp0, b_p) - x_k

    """
    2   Get SEN information.
    """
    # t_sen
    # t_sen < y_m / 4 *** conditional expression ***
    max_t_sen = y_m / 4
    max_t_sen = int(max_t_sen)

    # message
    message = "Max mateiral thickness to cut SEN is %s. \
    Enter the number less than max thickness of SEN." % max_t_sen

    rs.MessageBox(message, 0, "SEN_information")

    t_sen = rs.GetReal("Put Int or Real of thickness of material to cut sen (1layer)")
    if t_sen > max_t_sen:
        sys.exit()
    else:
        pass

    # Automatically fixed---------------------------------------------------
    w_sen = t_sen
    n_w_sen = w_sen / 2
    h_sen = z_m
    # t_sen = w_sen

    l_max_n = l_distance / (2 * w_sen - n_w_sen)      # NOTE: divide max_n by 2 to controll "n"
    l_max_n = int(l_max_n)

    l_n = l_max_n / 3
    l_n = int(l_n)

    r_max_n = r_distance / (2 * w_sen - n_w_sen)      # NOTE: divide max_n by 2 to controll "n"
    r_max_n = int(r_max_n)

    r_n = r_max_n / 3
    r_n = int(r_n)

    if l_n == 1 and r_n == 1:
        print ('l_n and r_n == 1')
        set = 15
        l_offset = 0
        r_offset = 0
        pass

    elif l_n == 1:
        print ('l_n = 1')
        set = 15
        l_offset = 0
        r_offset = (r_distance - 2 * set) / (r_n - 1)

        pass

    elif r_n == 1:
        print ('r_n = 1')
        set = 15
        l_offset = (l_distance - 2 * set) / (l_n - 1)
        r_offset = 0
        pass

    else:
        print (['l_n = %s' % l_n, 'r_n = %s' % r_n])
        set = 15
        l_offset = (l_distance - 2 * set) / (l_n - 1)
        r_offset = (r_distance - 2 * set) / (r_n - 1)

    SEN_info = [w_sen, n_w_sen, h_sen, t_sen, l_n, r_n, set, l_offset, r_offset]

    return SEN_info

def get_SHIGUCHI_SEN_info(dx, dy, KUMIKI_info, x_k):
    """Gets information of SHIGUCHI SEN.
    Receives:
        (dx, dy)        pt      Base point to make KUMIKI
        x_k             int     x length of KUMIKI

        KUMIKI_info     list    list of information
                                [m_info, m_model]
        m_info                  [x_m, y_m, z_m, m_points, layer_t]
        m_points                [l_mp0, l_mp1, r_mp0, r_mp1]

        x_m             int     x length of material
        y_m             int     y length of material
        z_m             int     z length of material

    Returns:
        SEN_info        list    list of SEN information
                                [w_sen, n_w_sen, h_sen, t_sen,
                                 l_n, r_n, set, l_offset, r_offset]

        w_sen           int     width of sen
        n_w_sen         int     narrow part width of sen
        h_sen           int     height of sen
        t_sen           int     thickness of sen

        n1              int     the number of sen of material1
        n2              int     the number of sen of material2
        set             int     the number of setback from edge line of material to line up SEN
        offset1         int     the number of offset between each SENs
        offset2         int     the number of offset between each SENs

    1   Get parameters from KUMIKI_info
    """
    m1_info = KUMIKI_info[0]
    m2_info = KUMIKI_info[1]

    # material1
    x_m1 = m1_info[0]
    y_m1 = m1_info[1]
    z_m = m1_info[2]

    m1_points = m1_info[3]
    m1_p0 = m1_points[0]
    m1_p1 = m1_points[1]
    m1_p2 = m1_points[2]
    m1_p3 = m1_points[3]

    # material2
    x_m2 = m2_info[0]
    x_m2 = abs(x_m2)
    y_m2 = m2_info[1]
    y_m2 = abs(y_m2)

    m2_points = m2_info[3]
    m2_p0 = m2_points[0]
    m2_p1 = m2_points[1]
    m2_p2 = m2_points[2]
    m2_p3 = m2_points[3]

    """
    2   Get SEN information.
    """
    message = "Put the SEN information"
    rs.MessageBox(message, 0, 'SEN information')

    # t_sen
    # t_sen < y_m1 / 4 *** conditional expression ***
    max_t_sen = y_m1 / 4
    max_t_sen = int(max_t_sen)

    # message
    message = "Max thickness of SEN is %s.\
    Enter the number less than max thickness of SEN."  % max_t_sen

    rs.MessageBox(message, 0, "t_sen")

    t_sen = rs.GetReal("Put Int or Real of thickness of material to cut sen (1layer)")
    if t_sen > max_t_sen:
        sys.exit()
    else:
        pass

    # Automatically fixed---------------------------------------------------
    w_sen = t_sen
    n_w_sen = w_sen / 2
    h_sen = z_m
    # t_sen = w_sen

    max_n1 = x_m1 / (2 * w_sen - n_w_sen) / 2       # NOTE: divide max_n by 2 to controll "n"
    max_n1 = int(max_n1)

    n1 = max_n1 / 3
    n1 = int(n1)

    max_n2 = y_m2 / (2 * w_sen - n_w_sen) / 2       # NOTE: divide max_n by 2 to controll "n"
    max_n2 = int(max_n2)

    n2 = max_n2 / 3
    n2 = int(n2)

    if n1 == 1 and n2 == 1:
        print ('n1 and n2 == 1')
        set = 15
        offset1 = 0
        offset2 = 0

    elif n1 == 1:
        print ('n1 = 1')
        set = 15
        offset1 = 0
        offset2 = (y_m2 - 2 * set) / (n2 - 1)

    elif n2 == 1:
        print('n2 = 1')
        set = 15
        offset1 = (x_m1 - 2 * set) / (n1 - 1)
        offset2 = 0

    else:
        print (['n1 = %s' % n1, 'n2 = %s' % n2])
        set = 15
        offset1 = (x_m1 - 2 * set) / (n1 - 1)
        offset2 = (y_m2 - 2 * set) / (n2 - 1)

    SEN_info = [w_sen, n_w_sen, h_sen, t_sen, n1, n2, set, offset1, offset2]

    return SEN_info

# upper shape-------------------------------------------------------------------
def X_upper_shape_points(ix, iy, w_sen, t_sen, n_w_sen):
    """Make list of X direction upper shapes points.
    Receives:
        (ix, iy)        point   Base point of shape.
            w_sen       int     x length of sen
            n_w_sen     int     narrow part x length of sen
            t_sen       int     z length of sen (thickness of sen)
    Returns:
            points
    """
    p0 = (ix, iy)
    p1 = (ix - w_sen + n_w_sen / 2, iy - t_sen)
    p2 = (ix - w_sen + n_w_sen / 2, iy)
    p3 = (ix - n_w_sen / 2, iy)
    p4 = (ix - n_w_sen / 2, iy + t_sen)
    p5 = (ix + w_sen - n_w_sen / 2, iy + t_sen)
    p6 = (ix + w_sen - n_w_sen / 2, iy)
    p7 = (ix + n_w_sen / 2, iy)
    p8 = (ix + n_w_sen / 2, iy - t_sen)

    return p0, p1, p2, p3, p4, p5, p6, p7, p8

def Y_upper_shape_points(ix, iy, w_sen, t_sen, n_w_sen):
    """Make list of Y direction upper shapes points.
    Receives:
        (ix, iy)        point   Base point of shape.
            w_sen       int     x length of sen
            n_w_sen     int     narrow part x length of sen
            t_sen       int     z length of sen (thickness of sen)
    Returns:
            points
    """
    p0 = (ix, iy)
    p1 = (ix - t_sen, iy - w_sen + n_w_sen / 2)
    p2 = (ix, iy - w_sen + n_w_sen / 2)
    p3 = (ix, iy - n_w_sen / 2)
    p4 = (ix + t_sen, iy - n_w_sen / 2)
    p5 = (ix + t_sen, iy + w_sen - n_w_sen / 2)
    p6 = (ix, iy + w_sen - n_w_sen / 2)
    p7 = (ix, iy + n_w_sen / 2)
    p8 = (ix - t_sen, iy + n_w_sen / 2)

    return p0, p1, p2, p3, p4, p5, p6, p7, p8

def TSUGITE_make_upper_shape_points_list(dx, dy, KUMIKI_info, SEN_info):
    """Make upper shape points list.
    Receives:
        (dx, dy)        pt      Base point to make KUMIKI
        KUMIKI_info     list    Information of KUMIKI to make
                                [m_info, m_model]
        m_info          list    list of material information
                                [x_m, y_m, z_m, m_points, layer_t]
        m_points        list    list of material points
                                [l_mp0, l_mp1, r_mp0, r_mp1]
        SEN_info        list    list of SEN information
                                [w_sen, n_w_sen, h_sen, t_sen,
                                 l_n, r_n, set, l_offset, r_offset]
    Returns:
        upper_shape_left    list        leftside upper_shape
                                        [upper_shape_left_upper_row, upper_shape_left_lower_row]
        upper_shape_right   list        rightside upper_shape
                                        [upper_shape_right_upper_row, upper_shape_right_lower_row]

        upper_shape_left_upper_row      list
        upper_shape_left_lower_row      list

        upper_shape_right_upper_row     list
        upper_shape_right_lower_row     list

    1   Get paramters from list.
    """
    m_info = KUMIKI_info[0]

    x_m = m_info[0]
    y_m = m_info[1]
    z_m = m_info[2]

    w_sen = SEN_info[0]
    n_w_sen = SEN_info[1]
    h_sen = SEN_info[2]
    t_sen = SEN_info[3]
    l_n = SEN_info[4]
    r_n = SEN_info[5]
    set = SEN_info[6]
    l_offset = SEN_info[7]
    r_offset = SEN_info[8]

    """
    2   Make lists.
        upper_shape_left_upper_row      list
        upper_shape_left_lower_row      list

        upper_shape_right_upper_row     list
        upper_shape_right_lower_row     list
    """
    # Leftside
    upper_shape_left_upper_row = []
    upper_shape_left_lower_row = []

    for i in range(l_n):
        # upper row
        ix = i * l_offset + set
        iy = y_m - t_sen
        p0, p1, p2, p3, p4, p5, p6, p7, p8 = X_upper_shape_points(ix, iy, w_sen, t_sen, n_w_sen)
        upper_points = [p4, p3, p2, p1, p8, p7, p6, p5]
        upper_shape_left_upper_row.extend((upper_points))

    for i in range(l_n - 1, -1, -1):
        # lower row
        ix = i * l_offset + set
        iy = t_sen
        p0, p1, p2, p3, p4, p5, p6, p7, p8 = X_upper_shape_points(ix, iy, w_sen, t_sen, n_w_sen)
        lower_points = [p8, p7, p6, p5, p4, p3, p2, p1]
        upper_shape_left_lower_row.extend(lower_points)

    # Rightside
    upper_shape_right_upper_row = []
    upper_shape_right_lower_row = []

    for i in range(r_n):
        # upper row
        ix = x_m - i * r_offset - set
        iy = y_m - t_sen
        p0, p1, p2, p3, p4, p5, p6, p7, p8 = X_upper_shape_points(ix, iy, w_sen, t_sen, n_w_sen)
        upper_points = [p5, p6, p7, p8, p1, p2, p3, p4]
        upper_shape_right_upper_row.extend((upper_points))

    for i in range(r_n - 1, -1, -1):
        # lower row
        ix = x_m - i * r_offset - set
        iy = t_sen
        p0, p1, p2, p3, p4, p5, p6, p7, p8 = X_upper_shape_points(ix, iy, w_sen, t_sen, n_w_sen)
        lower_points = [p1, p2, p3, p4, p5, p6, p7, p8]
        upper_shape_right_lower_row.extend(lower_points)

    upper_shape_left = [upper_shape_left_upper_row, upper_shape_left_lower_row]
    upper_shape_right = [upper_shape_right_upper_row, upper_shape_right_lower_row]

    return upper_shape_left, upper_shape_right

def SHIGUCHI_make_upper_shape_points_list(dx, dy, KUMIKI_info, SEN_info):
    """Make SHIGUCHI upper shape points list.
    Receives:
        (dx, dy)        pt      Base point to make KUMIKI
        KUMIKI_info     list    Information of KUMIKI to make
                                [m1_info, m2_info, m1_model, m2_model, direction]
        m1_info         list    list of material1 information
                                [x_m1, y_m1, z_m, m1_points]
        m2_info         list    list of material2 information
                                [x_m2, y_m2, z_m, m2_points]
        m1_points       list    list of material1 points
                                [m1_p0, m1_p1, m1_p2, m1_p3]
        m2_points       list    list of material2 points
                                [m2_p0, m2_p1, m2_p2, m2_p3]

        SEN_info        list    list of SEN information
                                [w_sen, n_w_sen, h_sen, t_sen,
                                 n1, n2, set, offset1, offset2]
    Returns:
        upper_shape_m1                  list        material1 upper_shape
                                                    [upper_shape_m1_upper_row, upper_shape_m1_lower_row]
        upper_shape_m2                  list        material2 upper_shape
                                                    [upper_shape_m2_upper_row, upper_shape_m2_lower_row]

        upper_shape_m1_upper_row        list
        upper_shape_m1_lower_row        list

        upper_shape_m2_upper_row        list
        upper_shape_m2_lower_row        list

    1   Get parameters from list.
    """
    m1_info = KUMIKI_info[0]
    m2_info = KUMIKI_info[1]
    direction = KUMIKI_info[4]

    # material1
    x_m1 = m1_info[0]
    y_m1 = m1_info[1]
    z_m = m1_info[2]

    # material2
    x_m2 = m2_info[0]
    x_m2 = abs(x_m2)
    y_m2 = m2_info[1]
    y_m2 = abs(y_m2)

    w_sen = SEN_info[0]
    n_w_sen = SEN_info[1]
    h_sen = SEN_info[2]
    t_sen = SEN_info[3]
    n1 = SEN_info[4]
    n2 = SEN_info[5]
    set = SEN_info[6]
    offset1 = SEN_info[7]
    offset2 = SEN_info[8]

    """
    2   Make lists.
        upper_shape_m1_upper_row    list
        upper_shape_m1_lower_row    list

        upper_shape_m2_upper_row    list
        upper_shape_m2_lower_row    list
    """
    # material1
    upper_shape_m1_upper_row = []
    upper_shape_m1_lower_row = []

    # material2
    upper_shape_m2_upper_row = []
    upper_shape_m2_lower_row = []


    if direction == 'UpperRight':
        # material1
        for i in range(n1):
            ix = i * offset1 + set
            iy = t_sen

            p0, p1, p2, p3, p4, p5, p6, p7, p8 = X_upper_shape_points(ix, iy, w_sen, t_sen, n_w_sen)
            upper_points = [p1, p2, p3, p4, p5, p6, p7, p8]
            upper_shape_m1_upper_row.extend((upper_points))

        for i in range(n1 - 1, -1, -1):
            ix = i * offset1 + set
            iy = y_m1 - t_sen

            p0, p1, p2, p3, p4, p5, p6, p7, p8 = X_upper_shape_points(ix, iy, w_sen, t_sen, n_w_sen)
            lower_points = [p5, p6, p7, p8, p1, p2, p3, p4]
            upper_shape_m1_lower_row.extend(lower_points)

        # material2
        for i in range(n2 -1 , -1, -1):
            ix = dx + (x_m2 - t_sen)
            iy = dy + (i * offset2 + set)

            p0, p1, p2, p3, p4, p5, p6, p7, p8 = Y_upper_shape_points(ix, iy, w_sen, t_sen, n_w_sen)
            upper_points = [p5, p6, p7, p8, p1, p2, p3, p4]
            upper_shape_m2_upper_row.extend((upper_points))

        for i in range(n2):
            ix = dx + t_sen
            iy = dy + (i * offset2 + set)

            p0, p1, p2, p3, p4, p5, p6, p7, p8 = Y_upper_shape_points(ix, iy, w_sen, t_sen, n_w_sen)
            lower_points = [p1, p2, p3, p4, p5, p6, p7, p8]
            upper_shape_m2_lower_row.extend(lower_points)

    elif direction == 'LowerRight':
        # material1
        for i in range(n1):
            ix = i * offset1 + set
            iy = y_m1 - t_sen

            p0, p1, p2, p3, p4, p5, p6, p7, p8 = X_upper_shape_points(ix, iy, w_sen, t_sen, n_w_sen)
            upper_points = [p4, p3, p2, p1, p8, p7, p6, p5]
            upper_shape_m1_upper_row.extend((upper_points))

        for i in range(n1 - 1, -1, -1):
            ix = i * offset1 + set
            iy = t_sen

            p0, p1, p2, p3, p4, p5, p6, p7, p8 = X_upper_shape_points(ix, iy, w_sen, t_sen, n_w_sen)
            lower_points = [p8, p7, p6, p5, p4, p3, p2, p1]
            upper_shape_m1_lower_row.extend(lower_points)

        # material2
        for i in range(n2 - 1, -1, -1):
            ix = dx + (x_m2 - t_sen)
            iy = dy - (i * offset2 + set)

            p0, p1, p2, p3, p4, p5, p6, p7, p8 = Y_upper_shape_points(ix, iy, w_sen, t_sen, n_w_sen)
            upper_points = [p4, p3, p2, p1, p8, p7, p6, p5]
            upper_shape_m2_upper_row.extend((upper_points))

        for i in range(n2):
            ix = dx + t_sen
            iy = dy - (i * offset2 + set)

            p0, p1, p2, p3, p4, p5, p6, p7, p8 = Y_upper_shape_points(ix, iy, w_sen, t_sen, n_w_sen)
            lower_points = [p8, p7, p6, p5, p4, p3, p2, p1]
            upper_shape_m2_lower_row.extend(lower_points)

    elif direction == 'UpperLeft':
        # material1
        for i in range(n1 - 1, -1, -1):
            ix = i * offset1 + set
            iy = t_sen

            p0, p1, p2, p3, p4, p5, p6, p7, p8 = X_upper_shape_points(ix, iy, w_sen, t_sen, n_w_sen)
            upper_points = [p8, p7, p6, p5, p4, p3, p2, p1]
            upper_shape_m1_upper_row.extend((upper_points))

        for i in range(n1):
            ix = i * offset1 + set
            iy = y_m1 - t_sen

            p0, p1, p2, p3, p4, p5, p6, p7, p8 = X_upper_shape_points(ix, iy, w_sen, t_sen, n_w_sen)
            lower_points = [p4, p3, p2, p1, p8, p7, p6, p5]
            upper_shape_m1_lower_row.extend(lower_points)

        # material2
        for i in range(n2 - 1, -1, -1):
            ix = dx - (x_m2 - t_sen)
            iy = dy + (i * offset2 + set)

            p0, p1, p2, p3, p4, p5, p6, p7, p8 = Y_upper_shape_points(ix, iy, w_sen, t_sen, n_w_sen)
            upper_points = [p8, p7, p6, p5, p4, p3, p2, p1]
            upper_shape_m2_upper_row.extend((upper_points))

        for i in range(n2):
            ix = dx - t_sen
            iy = dy + (i * offset2 + set)

            p0, p1, p2, p3, p4, p5, p6, p7, p8 = Y_upper_shape_points(ix, iy, w_sen, t_sen, n_w_sen)
            lower_points = [p4, p3, p2, p1, p8, p7, p6, p5]
            upper_shape_m2_lower_row.extend(lower_points)

    elif direction == 'LowerLeft':
        # material1
        for i in range(n1 - 1, -1, -1):
            ix = i * offset1 + set
            iy = y_m1 - t_sen

            p0, p1, p2, p3, p4, p5, p6, p7, p8 = X_upper_shape_points(ix, iy, w_sen, t_sen, n_w_sen)
            upper_points = [p5, p6, p7, p8, p1, p2, p3, p4]
            upper_shape_m1_upper_row.extend((upper_points))

        for i in range(n1):
            ix = i * offset2 + set
            iy = t_sen

            p0, p1, p2, p3, p4, p5, p6, p7, p8 = X_upper_shape_points(ix, iy, w_sen, t_sen, n_w_sen)
            lower_points = [p1, p2, p3, p4, p5, p6, p7, p8]
            upper_shape_m1_lower_row.extend(lower_points)

        # material2
        for i in range(n2 - 1, -1, -1):
            ix = dx - (x_m2 - t_sen)
            iy = dy - (i * offset2 + set)

            p0, p1, p2, p3, p4, p5, p6, p7, p8 = Y_upper_shape_points(ix, iy, w_sen, t_sen, n_w_sen)
            upper_points = [p1, p2, p3, p4, p5, p6, p7, p8]
            upper_shape_m2_upper_row.extend((upper_points))

        for i in range(n2):
            ix = dx - t_sen
            iy = dy - (i * offset2 + set)

            p0, p1, p2, p3, p4, p5, p6, p7, p8 = Y_upper_shape_points(ix, iy, w_sen, t_sen, n_w_sen)
            lower_points = [p5, p6, p7, p8, p1, p2, p3, p4]
            upper_shape_m2_lower_row.extend(lower_points)

    else:
        sys.exit()

    upper_shape_m1 = [upper_shape_m1_upper_row, upper_shape_m1_lower_row]
    upper_shape_m2 = [upper_shape_m2_upper_row, upper_shape_m2_lower_row]

    return upper_shape_m1, upper_shape_m2

# lower shape-------------------------------------------------------------------
def X_lower_shape_points(ix, iy, w_sen, t_sen, n_w_sen):
    """Make list of X direction lower shapes points.
    Receives:
        (ix, iy)       point   Base point of shape.
            w_sen      int     x length of sen
            n_w_sen    int     narrow part x length of sen
            t_sen      int     z length of sen (thickness of sen)
    Returns:
            points
    """
    p0 = (ix, iy)
    p1 = (ix - w_sen + n_w_sen / 2, iy + t_sen)
    p2 = (ix - w_sen + n_w_sen / 2, iy)
    p3 = (ix - n_w_sen / 2, iy)
    p4 = (ix - n_w_sen / 2, iy - t_sen)
    p5 = (ix + w_sen - n_w_sen / 2, iy - t_sen)
    p6 = (ix + w_sen - n_w_sen / 2, iy)
    p7 = (ix + n_w_sen / 2, iy)
    p8 = (ix + n_w_sen / 2, iy + t_sen)

    return p0, p1, p2, p3, p4, p5, p6, p7, p8

def Y_lower_shape_points(ix, iy, w_sen, t_sen, n_w_sen):
    """Make list of Y direction lower shapes points.
    Receives:
        (ix, iy)       point   Base point of shape.
            w_sen      int     x length of sen
            n_w_sen    int     narrow part x length of sen
            t_sen      int     z length of sen (thickness of sen)
    Returns:
            points
    """
    p0 = (ix, iy)
    p1 = (ix + t_sen, iy - w_sen + n_w_sen / 2)
    p2 = (ix, iy - w_sen + n_w_sen / 2)
    p3 = (ix, iy - n_w_sen / 2)
    p4 = (ix - t_sen, iy - n_w_sen / 2)
    p5 = (ix - t_sen, iy + w_sen - n_w_sen / 2)
    p6 = (ix, iy + w_sen - n_w_sen / 2)
    p7 = (ix, iy + n_w_sen / 2)
    p8 = (ix + t_sen, iy + n_w_sen / 2)

    return p0, p1, p2, p3, p4, p5, p6, p7, p8

def TSUGITE_make_lower_shape_points_list(dx, dy, KUMIKI_info, SEN_info):
    """Make lower shape points list.
    Receives:
        (dx, dy)        pt      Base point to make KUMIKI
        KUMIKI_info     list    Information of KUMIKI to make
                                [m_info, m_model]
        m_info          list    list of material information
                                [x_m, y_m, z_m, m_points, layer_t]
        m_points        list    list of material points
                                [l_mp0, l_mp1, r_mp0, r_mp1]
        SEN_info        list    list of SEN information
                                [w_sen, n_w_sen, h_sen, t_sen,
                                 l_n, r_n, set, l_offset, r_offset]

    Returns:
        lower_shape_left    list        leftside lower_shape
                                        [lower_shape_left_upper_row, lower_shape_left_lower_row]
        lower_shape_right   list        rightside lower_shape
                                        [lower_shape_right_upper_row, lower_shape_right_lower_row]

        lower_shape_left_upper_row      list
        lower_shape_left_lower_row      list

        lower_shape_right_upper_row     list
        lower_shape_right_lower_row     list

    1   Get parameters from list.
    """
    m_info = KUMIKI_info[0]

    x_m = m_info[0]
    y_m = m_info[1]
    z_m = m_info[2]

    w_sen = SEN_info[0]
    n_w_sen = SEN_info[1]
    h_sen = SEN_info[2]
    t_sen = SEN_info[3]
    l_n = SEN_info[4]
    r_n = SEN_info[5]
    set = SEN_info[6]
    l_offset = SEN_info[7]
    r_offset = SEN_info[8]

    """
    2   Make lists.
        lower_shape_left_upper_row      list
        lower_shape_left_lower_row      list

        lower_shape_right_upper_row     list
        lower_shape_right_lower_row     list
    """
    # Leftside
    lower_shape_left_upper_row = []
    lower_shape_left_lower_row = []

    for i in range(l_n):
        # upper row
        ix = i * l_offset + set
        iy = y_m - t_sen
        p0, p1, p2, p3, p4, p5, p6, p7, p8 = X_lower_shape_points(ix, iy, w_sen, t_sen, n_w_sen)
        upper_points = [p1, p2, p3, p4, p5, p6, p7, p8]
        lower_shape_left_upper_row.extend((upper_points))

    for i in range(l_n - 1, -1, -1):
        # lower row
        ix = i * l_offset + set
        iy = t_sen
        p0, p1, p2, p3, p4, p5, p6, p7, p8 = X_lower_shape_points(ix, iy, w_sen, t_sen, n_w_sen)
        lower_points = [p5, p6, p7, p8, p1, p2, p3, p4]
        lower_shape_left_lower_row.extend(lower_points)

    # Rightside
    lower_shape_right_upper_row = []
    lower_shape_right_lower_row = []

    for i in range(r_n):
        # upper row
        ix = x_m - i * r_offset - set
        iy = y_m - t_sen
        p0, p1, p2, p3, p4, p5, p6, p7, p8 = X_lower_shape_points(ix, iy, w_sen, t_sen, n_w_sen)
        upper_points = [p8, p7, p6, p5, p4, p3, p2, p1]
        lower_shape_right_upper_row.extend((upper_points))

    for i in range(r_n - 1, -1, -1):
        # lower row
        ix = x_m - i * r_offset - set
        iy = t_sen
        p0, p1, p2, p3, p4, p5, p6, p7, p8 = X_lower_shape_points(ix, iy, w_sen, t_sen, n_w_sen)
        lower_points = [p4, p3, p2, p1, p8, p7, p6, p5]
        lower_shape_right_lower_row.extend(lower_points)

    lower_shape_left = [lower_shape_left_upper_row, lower_shape_left_lower_row]
    lower_shape_right = [lower_shape_right_upper_row, lower_shape_right_lower_row]

    return lower_shape_left, lower_shape_right

def SHIGUCHI_make_lower_shape_points_list(dx, dy, KUMIKI_info, SEN_info):
    """Make SHIGUCHI lower shape points list.
    Receives:
        (dx, dy)        pt      Base point to make KUMIKI
        KUMIKI_info     list    Information of KUMIKI to make
                                [m1_info, m2_info, m1_model, m2_model, direction]
        m1_info         list    list of material1 information
                                [x_m1, y_m1, z_m, m1_points]
        m2_info         list    list of material2 information
                                [x_m2, y_m2, z_m, m2_points]
        m1_points       list    list of material1 points
                                [m1_p0, m1_p1, m1_p2, m1_p3]
        m2_points       list    list of material2 points
                                [m2_p0, m2_p1, m2_p2, m2_p3]

        SEN_info        list    list of SEN information
                                [w_sen, n_w_sen, h_sen, t_sen,
                                 n1, n2, set, offset1, offset2]
    Returns:
        lower_shape_m1                  list        material1 lower_shape
                                                    [lower_shape_m1_upper_row, lower_shape_m1_lower_row]
        lower_shape_m2                  list        material2 lower_shape
                                                    [lower_shape_m2_upper_row, lower_shape_m2_lower_row]

        lower_shape_m1_upper_row        list
        lower_shape_m1_lower_row        list

        lower_shape_m2_upper_row        list
        lower_shape_m2_lower_row        list

    1   Get parameters from list.
    """
    m1_info = KUMIKI_info[0]
    m2_info = KUMIKI_info[1]
    direction = KUMIKI_info[4]

    # material1
    x_m1 = m1_info[0]
    y_m1 = m1_info[1]
    z_m = m1_info[2]

    # material2
    x_m2 = m2_info[0]
    x_m2 = abs(x_m2)
    y_m2 = m2_info[1]
    y_m2 = abs(y_m2)

    w_sen = SEN_info[0]
    n_w_sen = SEN_info[1]
    h_sen = SEN_info[2]
    t_sen = SEN_info[3]
    n1 = SEN_info[4]
    n2 = SEN_info[5]
    set = SEN_info[6]
    offset1 = SEN_info[7]
    offset2 = SEN_info[8]

    """
    2   Make lists.
        lower_shape_m1_upper_row    list
        lower_shape_m1_lower_row    list

        lower_shape_m2_upper_row    list
        lower_shape_m2_lower_row    list
    """
    # material1
    lower_shape_m1_upper_row = []
    lower_shape_m1_lower_row = []

    # material2
    lower_shape_m2_upper_row = []
    lower_shape_m2_lower_row = []

    if direction == 'UpperRight':
        # material1
        for i in range(n1):
            ix = i * offset1 + set
            iy = t_sen

            p0, p1, p2, p3, p4, p5, p6, p7, p8 = X_lower_shape_points(ix, iy, w_sen, t_sen, n_w_sen)
            upper_points = [p4, p3, p2, p1, p8, p7, p6, p5]
            lower_shape_m1_upper_row.extend((upper_points))

        for i in range(n1 - 1, -1, -1):
            ix = i * offset1 + set
            iy = y_m1 - t_sen

            p0, p1, p2, p3, p4, p5, p6, p7, p8 = X_lower_shape_points(ix, iy, w_sen, t_sen, n_w_sen)
            lower_points = [p8, p7, p6, p5, p4, p3, p2, p1]
            lower_shape_m1_lower_row.extend(lower_points)

        # material2
        for i in range(n2 -1 , -1, -1):
            ix = dx + (x_m2 - t_sen)
            iy = dy + (i * offset2 + set)

            p0, p1, p2, p3, p4, p5, p6, p7, p8 = Y_lower_shape_points(ix, iy, w_sen, t_sen, n_w_sen)
            upper_points = [p8, p7, p6, p5, p4, p3, p2, p1]
            lower_shape_m2_upper_row.extend((upper_points))

        for i in range(n2):
            ix = dx + t_sen
            iy = dy + (i * offset2 + set)

            p0, p1, p2, p3, p4, p5, p6, p7, p8 = Y_lower_shape_points(ix, iy, w_sen, t_sen, n_w_sen)
            lower_points = [p4, p3, p2, p1, p8, p7, p6, p5]
            lower_shape_m2_lower_row.extend(lower_points)

    elif direction == 'LowerRight':
        # material1
        for i in range(n1):
            ix = i * offset1 + set
            iy = y_m1 - t_sen

            p0, p1, p2, p3, p4, p5, p6, p7, p8 = X_lower_shape_points(ix, iy, w_sen, t_sen, n_w_sen)
            upper_points = [p1, p2, p3, p4, p5, p6, p7, p8]
            lower_shape_m1_upper_row.extend((upper_points))

        for i in range(n1 - 1, -1, -1):
            ix = i * offset1 + set
            iy = t_sen

            p0, p1, p2, p3, p4, p5, p6, p7, p8 = X_lower_shape_points(ix, iy, w_sen, t_sen, n_w_sen)
            lower_points = [p5, p6, p7, p8, p1, p2, p3, p4]
            lower_shape_m1_lower_row.extend(lower_points)

        # material2
        for i in range(n2 - 1, -1, -1):
            ix = dx + (x_m2 - t_sen)
            iy = dy - (i * offset2 + set)

            p0, p1, p2, p3, p4, p5, p6, p7, p8 = Y_lower_shape_points(ix, iy, w_sen, t_sen, n_w_sen)
            upper_points = [p1, p2, p3, p4, p5, p6, p7, p8]
            lower_shape_m2_upper_row.extend((upper_points))

        for i in range(n2):
            ix = dx + t_sen
            iy = dy - (i * offset2 + set)

            p0, p1, p2, p3, p4, p5, p6, p7, p8 = Y_lower_shape_points(ix, iy, w_sen, t_sen, n_w_sen)
            lower_points = [p5, p6, p7, p8, p1, p2, p3, p4]
            lower_shape_m2_lower_row.extend(lower_points)

    elif direction == 'UpperLeft':
        # material1
        for i in range(n1 - 1, -1, -1):
            ix = i * offset1 + set
            iy = t_sen

            p0, p1, p2, p3, p4, p5, p6, p7, p8 = X_lower_shape_points(ix, iy, w_sen, t_sen, n_w_sen)
            upper_points = [p5, p6, p7, p8, p1, p2, p3, p4]
            lower_shape_m1_upper_row.extend((upper_points))

        for i in range(n1):
            ix = i * offset1 + set
            iy = y_m1 - t_sen

            p0, p1, p2, p3, p4, p5, p6, p7, p8 = X_lower_shape_points(ix, iy, w_sen, t_sen, n_w_sen)
            lower_points = [p1, p2, p3, p4, p5, p6, p7, p8]
            lower_shape_m1_lower_row.extend(lower_points)

        # material2
        for i in range(n2 - 1, -1, -1):
            ix = dx - (x_m2 - t_sen)
            iy = dy + (i * offset2 + set)

            p0, p1, p2, p3, p4, p5, p6, p7, p8 = Y_lower_shape_points(ix, iy, w_sen, t_sen, n_w_sen)
            upper_points = [p5, p6, p7, p8, p1, p2, p3, p4]
            lower_shape_m2_upper_row.extend((upper_points))

        for i in range(n2):
            ix = dx - t_sen
            iy = dy + (i * offset2 + set)

            p0, p1, p2, p3, p4, p5, p6, p7, p8 = Y_lower_shape_points(ix, iy, w_sen, t_sen, n_w_sen)
            lower_points = [p1, p2, p3, p4, p5, p6, p7, p8]
            lower_shape_m2_lower_row.extend(lower_points)

    elif direction == 'LowerLeft':
        # material1
        for i in range(n1 - 1, -1, -1):
            ix = i * offset1 + set
            iy = y_m1 - t_sen

            p0, p1, p2, p3, p4, p5, p6, p7, p8 = X_lower_shape_points(ix, iy, w_sen, t_sen, n_w_sen)
            upper_points = [p8, p7, p6, p5, p4, p3, p2, p1]
            lower_shape_m1_upper_row.extend((upper_points))

        for i in range(n1):
            ix = i * offset2 + set
            iy = t_sen

            p0, p1, p2, p3, p4, p5, p6, p7, p8 = X_lower_shape_points(ix, iy, w_sen, t_sen, n_w_sen)
            lower_points = [p4, p3, p2, p1, p8, p7, p6, p5]
            lower_shape_m1_lower_row.extend(lower_points)

        # material2
        for i in range(n2 - 1, -1, -1):
            ix = dx - (x_m2 - t_sen)
            iy = dy - (i * offset2 + set)

            p0, p1, p2, p3, p4, p5, p6, p7, p8 = Y_lower_shape_points(ix, iy, w_sen, t_sen, n_w_sen)
            upper_points = [p4, p3, p2, p1, p8, p7, p6, p5]
            lower_shape_m2_upper_row.extend((upper_points))

        for i in range(n2):
            ix = dx - t_sen
            iy = dy - (i * offset2 + set)

            p0, p1, p2, p3, p4, p5, p6, p7, p8 = Y_lower_shape_points(ix, iy, w_sen, t_sen, n_w_sen)
            lower_points = [p8, p7, p6, p5, p4, p3, p2, p1]
            lower_shape_m2_lower_row.extend(lower_points)

    else:
        sys.exit()

    lower_shape_m1 = [lower_shape_m1_upper_row, lower_shape_m1_lower_row]
    lower_shape_m2 = [lower_shape_m2_upper_row, lower_shape_m2_lower_row]

    return lower_shape_m1, lower_shape_m2

# middle shape------------------------------------------------------------------
def X_middle_shape_points(ix, iy, w_sen, t_sen, n_w_sen):
    """Make list of middle shapes points.
    Receives:
        (ix, iy)       point   Base point of shape.
            w_sen      int     x length of sen
            n_w_sen    int     narrow part x length of sen
            t_sen      int     z length of sen (thickness of sen)
    Returns:
            points
    """
    p0 = (ix, iy)
    p1 = (ix - n_w_sen / 2, iy + t_sen)
    p2 = (ix - n_w_sen / 2, iy - t_sen)
    p3 = (ix + n_w_sen / 2, iy - t_sen)
    p4 = (ix + n_w_sen / 2, iy + t_sen)

    return p0, p1, p2, p3, p4

def Y_middle_shape_points(ix, iy, w_sen, t_sen, n_w_sen):
    """Make list of Y direction middle shapes points.
    Receives:
        (ix, iy)       point   Base point of shape.
            w_sen      int     x length of sen
            n_w_sen    int     narrow part x length of sen
            t_sen      int     z length of sen (thickness of sen)
    Returns:
            points
    """
    p0 = (ix, iy)
    p1 = (ix + t_sen, iy - n_w_sen / 2)
    p2 = (ix - t_sen, iy - n_w_sen / 2)
    p3 = (ix - t_sen, iy + n_w_sen / 2)
    p4 = (ix + t_sen, iy + n_w_sen / 2)

    return p0, p1, p2, p3, p4

def TSUGITE_make_middle_shape_points_list(dx, dy, KUMIKI_info, SEN_info):
    """Make middle shape points list.
    Receives:
        (dx, dy)        pt      Base point to make KUMIKI
        KUMIKI_info     list    Information of KUMIKI to make
                                [m_info, m_model]
        m_info          list    list of material information
                                [x_m, y_m, z_m, m_points, layer_t]
        m_points        list    list of material points
                                [l_mp0, l_mp1, r_mp0, r_mp1]
        SEN_info        list    list of SEN information
                                [w_sen, n_w_sen, h_sen, t_sen,
                                 l_n, r_n, set, l_offset, r_offset]

    Returns:
        middle_shape_m1    list     material1 middle_shape
                                    [middle_shape_m1_upper_row, middle_shape_m1_lower_row]
        middle_shape_m2   list      material2 middle_shape
                                    [middle_shape_m2_upper_row, middle_shape_m2_lower_row]

        middle_shape_m1_upper_row    list
        middle_shape_m1_lower_row    list

        middle_shape_m2_upper_row    list
        middle_shape_m2_lower_row    list

    1   Get parameters from list.
    """
    m_info = KUMIKI_info[0]

    x_m = m_info[0]
    y_m = m_info[1]
    z_m = m_info[2]

    w_sen = SEN_info[0]
    n_w_sen = SEN_info[1]
    h_sen = SEN_info[2]
    t_sen = SEN_info[3]
    l_n = SEN_info[4]
    r_n = SEN_info[5]
    set = SEN_info[6]
    l_offset = SEN_info[7]
    r_offset = SEN_info[8]

    """
    2   Make lists.
        middle_shape_m1_upper_row      list
        middle_shape_m1_lower_row      list

        middle_shape_m2_upper_row     list
        middle_shape_m2_lower_row     list
    """
    # material1
    middle_shape_m1_upper_row = []
    middle_shape_m1_lower_row = []

    for i in range(l_n):
        # upper row
        ix = i * l_offset + set
        iy = y_m - t_sen
        p0, p1, p2, p3, p4 = X_middle_shape_points(ix, iy, w_sen, t_sen, n_w_sen)
        upper_points = [p1, p2, p3, p4]
        middle_shape_m1_upper_row.extend((upper_points))

    for i in range(l_n - 1, -1, -1):
        # lower row
        ix = i * l_offset + set
        iy = t_sen
        p0, p1, p2, p3, p4 = X_middle_shape_points(ix, iy, w_sen, t_sen, n_w_sen)
        lower_points = [p3, p4, p1, p2]
        middle_shape_m1_lower_row.extend(lower_points)

    # material2
    middle_shape_m2_upper_row = []
    middle_shape_m2_lower_row = []

    for i in range(r_n):
        # upper row
        ix = x_m - i * r_offset - set
        iy = y_m - t_sen
        p0, p1, p2, p3, p4 = X_middle_shape_points(ix, iy, w_sen, t_sen, n_w_sen)
        upper_points = [p4, p3, p2, p1]
        middle_shape_m2_upper_row.extend((upper_points))

    for i in range(r_n - 1, -1, -1):
        # lower row
        ix = x_m - i * r_offset - set
        iy = t_sen
        p0, p1, p2, p3, p4 = X_middle_shape_points(ix, iy, w_sen, t_sen, n_w_sen)
        lower_points = [p2, p1, p4, p3]
        middle_shape_m2_lower_row.extend(lower_points)

    middle_shape_m1 = [middle_shape_m1_upper_row, middle_shape_m1_lower_row]
    middle_shape_m2 = [middle_shape_m2_upper_row, middle_shape_m2_lower_row]

    return middle_shape_m1, middle_shape_m2

def SHIGUCHI_make_middle_shape_points_list(dx, dy, KUMIKI_info, SEN_info):
    """Make SHIGUCHI middle shape points list.
    Receives:
        (dx, dy)        pt      Base point to make KUMIKI
        KUMIKI_info     list    Information of KUMIKI to make
                                [m1_info, m2_info, m1_model, m2_model, direction]
        m1_info         list    list of material1 information
                                [x_m1, y_m1, z_m, m1_points]
        m2_info         list    list of material2 information
                                [x_m2, y_m2, z_m, m2_points]
        m1_points       list    list of material1 points
                                [m1_p0, m1_p1, m1_p2, m1_p3]
        m2_points       list    list of material2 points
                                [m2_p0, m2_p1, m2_p2, m2_p3]

        SEN_info        list    list of SEN information
                                [w_sen, n_w_sen, h_sen, t_sen,
                                 n1, n2, set, offset1, offset2]
    Returns:
        middle_shape_m1                  list        material1 middle_shape
                                                    [middle_shape_m1_upper_row, middle_shape_m1_lower_row]
        middle_shape_m2                  list        material2 middle_shape
                                                    [middle_shape_m2_upper_row, middle_shape_m2_lower_row]

        middle_shape_m1_upper_row        list
        middle_shape_m1_lower_row        list

        middle_shape_m2_upper_row        list
        middle_shape_m2_lower_row        list

    1   Get parameters from list.
    """
    m1_info = KUMIKI_info[0]
    m2_info = KUMIKI_info[1]
    direction = KUMIKI_info[4]

    # material1
    x_m1 = m1_info[0]
    y_m1 = m1_info[1]
    z_m = m1_info[2]

    # material2
    x_m2 = m2_info[0]
    x_m2 = abs(x_m2)
    y_m2 = m2_info[1]
    y_m2 = abs(y_m2)

    w_sen = SEN_info[0]
    n_w_sen = SEN_info[1]
    h_sen = SEN_info[2]
    t_sen = SEN_info[3]
    n1 = SEN_info[4]
    n2 = SEN_info[5]
    set = SEN_info[6]
    offset1 = SEN_info[7]
    offset2 = SEN_info[8]

    """
    2   Make lists.
        middle_shape_m1_upper_row    list
        middle_shape_m1_lower_row    list

        middle_shape_m2_upper_row    list
        middle_shape_m2_lower_row    list
    """
    # material1
    middle_shape_m1_upper_row = []
    middle_shape_m1_lower_row = []

    # material2
    middle_shape_m2_upper_row = []
    middle_shape_m2_lower_row = []

    if direction == 'UpperRight':
        # material1
        for i in range(n1):
            ix = i * offset1 + set
            iy = t_sen

            p0, p1, p2, p3, p4 = X_middle_shape_points(ix, iy, w_sen, t_sen, n_w_sen)
            upper_points = [p2, p1, p4, p3]
            middle_shape_m1_upper_row.extend((upper_points))

        for i in range(n1 - 1, -1, -1):
            ix = i * offset1 + set
            iy = y_m1 - t_sen

            p0, p1, p2, p3, p4 = X_middle_shape_points(ix, iy, w_sen, t_sen, n_w_sen)
            lower_points = [p4, p3, p2, p1]
            middle_shape_m1_lower_row.extend(lower_points)

        # material2
        for i in range(n2 -1 , -1, -1):
            ix = dx + (x_m2 - t_sen)
            iy = dy + (i * offset2 + set)

            p0, p1, p2, p3, p4 = Y_middle_shape_points(ix, iy, w_sen, t_sen, n_w_sen)
            upper_points = [p4, p3, p2, p1]
            middle_shape_m2_upper_row.extend((upper_points))

        for i in range(n2):
            ix = dx + t_sen
            iy = dy + (i * offset2 + set)

            p0, p1, p2, p3, p4 = Y_middle_shape_points(ix, iy, w_sen, t_sen, n_w_sen)
            lower_points = [p2, p1, p4, p3]
            middle_shape_m2_lower_row.extend(lower_points)

    elif direction == 'LowerRight':
        # material1
        for i in range(n1):
            ix = i * offset1 + set
            iy = y_m1 - t_sen

            p0, p1, p2, p3, p4 = X_middle_shape_points(ix, iy, w_sen, t_sen, n_w_sen)
            upper_points = [p1, p2, p3, p4]
            middle_shape_m1_upper_row.extend((upper_points))

        for i in range(n1 - 1, -1, -1):
            ix = i * offset1 + set
            iy = t_sen

            p0, p1, p2, p3, p4 = X_middle_shape_points(ix, iy, w_sen, t_sen, n_w_sen)
            lower_points = [p3, p4, p1, p2]
            middle_shape_m1_lower_row.extend(lower_points)

        # material2
        for i in range(n2 - 1, -1, -1):
            ix = dx + (x_m2 - t_sen)
            iy = dy - (i * offset2 + set)

            p0, p1, p2, p3, p4 = Y_middle_shape_points(ix, iy, w_sen, t_sen, n_w_sen)
            upper_points = [p1, p2, p3, p4]
            middle_shape_m2_upper_row.extend((upper_points))

        for i in range(n2):
            ix = dx + t_sen
            iy = dy - (i * offset2 + set)

            p0, p1, p2, p3, p4 = Y_middle_shape_points(ix, iy, w_sen, t_sen, n_w_sen)
            lower_points = [p3, p4, p1, p2]
            middle_shape_m2_lower_row.extend(lower_points)

    elif direction == 'UpperLeft':
        # material1
        for i in range(n1 - 1, -1, -1):
            ix = i * offset1 + set
            iy = t_sen

            p0, p1, p2, p3, p4 = X_middle_shape_points(ix, iy, w_sen, t_sen, n_w_sen)
            upper_points = [p3, p4, p1, p2]
            middle_shape_m1_upper_row.extend((upper_points))

        for i in range(n1):
            ix = i * offset1 + set
            iy = y_m1 - t_sen

            p0, p1, p2, p3, p4 = X_middle_shape_points(ix, iy, w_sen, t_sen, n_w_sen)
            lower_points = [p1, p2, p3, p4]
            middle_shape_m1_lower_row.extend(lower_points)

        # material2
        for i in range(n2 - 1, -1, -1):
            ix = dx - (x_m2 - t_sen)
            iy = dy + (i * offset2 + set)

            p0, p1, p2, p3, p4 = Y_middle_shape_points(ix, iy, w_sen, t_sen, n_w_sen)
            upper_points = [p3, p4, p1, p2]
            middle_shape_m2_upper_row.extend((upper_points))

        for i in range(n2):
            ix = dx - t_sen
            iy = dy + (i * offset2 + set)

            p0, p1, p2, p3, p4 = Y_middle_shape_points(ix, iy, w_sen, t_sen, n_w_sen)
            lower_points = [p1, p2, p3, p4]
            middle_shape_m2_lower_row.extend(lower_points)

    elif direction == 'LowerLeft':
        # material1
        for i in range(n1 - 1, -1, -1):
            ix = i * offset1 + set
            iy = y_m1 - t_sen

            p0, p1, p2, p3, p4 = X_middle_shape_points(ix, iy, w_sen, t_sen, n_w_sen)
            upper_points = [p4, p3, p2, p1]
            middle_shape_m1_upper_row.extend((upper_points))

        for i in range(n1):
            ix = i * offset2 + set
            iy = t_sen

            p0, p1, p2, p3, p4 = X_middle_shape_points(ix, iy, w_sen, t_sen, n_w_sen)
            lower_points = [p2, p1, p4, p3]
            middle_shape_m1_lower_row.extend(lower_points)

        # material2
        for i in range(n2 - 1, -1, -1):
            ix = dx - (x_m2 - t_sen)
            iy = dy - (i * offset2 + set)

            p0, p1, p2, p3, p4 = Y_middle_shape_points(ix, iy, w_sen, t_sen, n_w_sen)
            upper_points = [p2, p1, p4, p3]
            middle_shape_m2_upper_row.extend((upper_points))

        for i in range(n2):
            ix = dx - t_sen
            iy = dy - (i * offset2 + set)

            p0, p1, p2, p3, p4 = Y_middle_shape_points(ix, iy, w_sen, t_sen, n_w_sen)
            lower_points = [p4, p3, p2, p1]
            middle_shape_m2_lower_row.extend(lower_points)

    else:
        sys.exit()

    middle_shape_m1 = [middle_shape_m1_upper_row, middle_shape_m1_lower_row]
    middle_shape_m2 = [middle_shape_m2_upper_row, middle_shape_m2_lower_row]

    return middle_shape_m1, middle_shape_m2

# For User----------------------------------------------------------------------
# SEN shape---------------------------------------------------------------------
def SEN_points(ix, iy, w_sen, n_w_sen, t_m, offset):
    """Make list of SEN points.
    Receives:
        (ix, iy)        num     Base point of SEN
        w_sen           int     x length of sen
        n_w_sen         int     narrow part x length of sen
        t_m             int     z length of material (thickness of material)
        offset          num     offset number to fit SEN tight
    Returns:
        points          list    list of SEN points.
    """
    p0 = (ix, iy)
    p1 = (ix - w_sen + n_w_sen / 2 - 3 * offset / 4, iy)
    p2 = (ix - w_sen + n_w_sen / 2 - 3 * offset / 4, iy + t_m)
    p3 = (ix - n_w_sen / 2 - offset / 4, iy + t_m)
    p4 = (ix - n_w_sen / 2 - offset / 4, iy + 3 * t_m)
    p5 = (ix + w_sen - n_w_sen / 2 + 3 * offset / 4, iy + 3 * t_m)
    p6 = (ix + w_sen - n_w_sen / 2 + 3 * offset / 4, iy + 2 * t_m)
    p7 = (ix + n_w_sen / 2 + offset / 4, iy + 2 * t_m)
    p8 = (ix + n_w_sen / 2 + offset / 4, iy)

    return p0, p1, p2, p3, p4, p5, p6, p7, p8

def make_SEN_crvs(KUMIKI_type, KUMIKI_info, SEN_info):
    """Make SEN crvs.
    Receives:
        KUMIKI_type     str     KUMIKI type
        KUMIKI_info     list    list of KUMIKI information
        SEN_info        list    list of SEN information
                                [w_sen, n_w_sen, h_sen, t_sen,
                                 l_n, r_n, set, l_offset, r_offset]
    Returns:
        SEN_crvs        list    list of SEN crvs
    """
    """
    1   Get information from SEN_info
    """
    if KUMIKI_type == 'TSUGITE':
        m_info = KUMIKI_info[0]
        x_m = m_info[0]
        y_m = m_info[1]

    elif KUMIKI_type == 'SHIGUCHI':
        m1_info = KUMIKI_info[0]
        x_m = x_m1 = m1_info[0]
        y_m = y_m1 = m1_info[1]

    else:
        sys.exit()

    w_sen = SEN_info[0]
    n_w_sen = SEN_info[1]
    h_sen = SEN_info[2]
    t_sen = SEN_info[3]

    t_m = h_sen / 3

    n1 = SEN_info[4]
    n2 = SEN_info[5]

    SEN_n = n1 + n2

    """
    2   Get offset num
    """
    minimum = 0
    maximum = 0.5

    offset = rs.GetReal("Put the offset num to fit SEN tight. (0.0 < offset < 0.5)",\
                        0.4, minimum, maximum)

    # NOTE: offset num is not parametric number. It's always fixed.

    """
    2   Make SEN_shapes.
    """
    SEN_shapes = []

    for j in range(3):
        for i in range(SEN_n):
            ix = i * 2 * (2 * w_sen - n_w_sen) + x_m + 2 * y_m
            iy = -1.5 * h_sen * (j + 1)
            p0, p1, p2, p3, p4, p5, p6, p7, p8 = SEN_points(ix, iy, w_sen, n_w_sen, t_m, offset)
            SEN_shape_list = [p1, p2, p3, p4, p5, p6, p7, p8, p1]
            SEN_shape = rs.AddPolyline(SEN_shape_list)
            SEN_shapes.append(SEN_shape)

        for i in range(SEN_n):
            ix = i * 2 * (2 * w_sen - n_w_sen) + x_m + 2 * y_m
            iy = -1.5 * h_sen * (j + 1) - 4.5 * h_sen
            p0, p1, p2, p3, p4, p5, p6, p7, p8 = SEN_points(ix, iy, w_sen, n_w_sen, t_m, offset)
            SEN_shape_list = [p1, p2, p3, p4, p5, p6, p7, p8, p1]
            SEN_shape = rs.AddPolyline(SEN_shape_list)
            SEN_shapes.append(SEN_shape)

    return SEN_shapes

# Deploy crvs (processing data)-------------------------------------------------
def deploy_crvs(KUMIKI_type, KUMIKI_info, crvs1, crvs2):
    """Deploy crvs.
    Receives:
        KUMIKI_type     str     KUMIKI type TSUGITE or SHIGUCHI
        KUMIKI_info     list    list of KUMIKI information
        crvs1           list    list of guids
        crvs2           list    ditto
    Returns:
        ---
    """
    if KUMIKI_type == 'TSUGITE':
        deploy_TSUGITE_crvs(KUMIKI_info, crvs1, crvs2)

    elif KUMIKI_type == 'SHIGUCHI':
        deploy_SHIGUCHI_crvs(KUMIKI_info, crvs1, crvs2)

    else:
        sys.exit()

    pass

def deploy_TSUGITE_crvs(KUMIKI_info, crvs1, crvs2):
    """Deploy crvs.
    Receives:
        KUMIKI_info     list    KUMIKI information
                                [m_info, m_model]
        m_info                  [x_m, y_m, z_m, m_points, layer_t]

        crvs1           list    list of guids [upper, middle, lower]
        crvs2           list    ditto
    Returns:
        ---
    """
    """
    1   Get information from list
    """
    m_info = KUMIKI_info[0]
    x_m = m_info[0]
    y_m = m_info[1]

    layer_t = m_info[4]
    l_n = len(layer_t)

    if l_n == 3:
        left_upper_crv = crvs1[0]
        left_middle_crv = crvs1[1]
        left_lower_crv = crvs1[2]

        right_upper_crv = crvs2[0]
        right_middle_crv = crvs2[1]
        right_lower_crv = crvs2[2]

        """
        2   Deploy crvs to user can pick up crv data.
        """
        # upper
        trans = (x_m + y_m, 3 * y_m, 0)
        rs.MoveObject(left_upper_crv, trans)

        trans = (x_m + 2.5 * y_m, 3 * y_m, 0)
        rs.MoveObject(right_upper_crv, trans)

        # middle
        trans = (x_m + y_m, 1.5 * y_m, 0)
        rs.MoveObject(left_middle_crv, trans)

        trans = (x_m + 2.5 * y_m, 1.5 * y_m, 0)
        rs.MoveObject(right_middle_crv, trans)

        # lower
        trans = (x_m + y_m, 0, 0)
        rs.MoveObject(left_lower_crv, trans)

        trans = (x_m + 2.5 * y_m, 0, 0)
        rs.MoveObject(right_lower_crv, trans)

    elif l_n == 4:
        left_upper_crv = crvs1[0]
        left_middle_crv1 = crvs1[1]
        left_middle_crv2 = crvs1[2]
        left_lower_crv = crvs1[3]

        right_upper_crv = crvs2[0]
        right_middle_crv1 = crvs2[1]
        right_middle_crv2 = crvs2[2]
        right_lower_crv = crvs2[3]

        """
        2   Deploy crvs to user can pick up crv data.
        """
        # upper
        trans = (x_m + y_m, 4.5 * y_m, 0)
        rs.MoveObject(left_upper_crv, trans)

        trans = (x_m + 2.5 * y_m, 4.5 * y_m, 0)
        rs.MoveObject(right_upper_crv, trans)

        # middle1
        trans = (x_m + y_m, 3 * y_m, 0)
        rs.MoveObject(left_middle_crv1, trans)

        trans = (x_m + 2.5 * y_m, 3 * y_m, 0)
        rs.MoveObject(right_middle_crv1, trans)

        # middle2
        trans = (x_m + y_m, 1.5 * y_m, 0)
        rs.MoveObject(left_middle_crv2, trans)

        trans = (x_m + 2.5 * y_m, 1.5 * y_m, 0)
        rs.MoveObject(right_middle_crv2, trans)

        # lower
        trans = (x_m + y_m, 0, 0)
        rs.MoveObject(left_lower_crv, trans)

        trans = (x_m + 2.5 * y_m, 0, 0)
        rs.MoveObject(right_lower_crv, trans)

    elif l_n == 5:
        left_upper_crv = crvs1[0]
        left_middle_crv1 = crvs1[1]
        left_middle_crv2 = crvs1[2]
        left_middle_crv3 = crvs1[3]
        left_lower_crv = crvs1[4]

        right_upper_crv = crvs2[0]
        right_middle_crv1 = crvs2[1]
        right_middle_crv2 = crvs2[2]
        right_middle_crv3 = crvs2[3]
        right_lower_crv = crvs2[4]

        """
        2   Deploy crvs to user can pick up crv data.
        """
        # upper
        trans = (x_m + y_m, 6 * y_m, 0)
        rs.MoveObject(left_upper_crv, trans)

        trans = (x_m + 2.5 * y_m, 6 * y_m, 0)
        rs.MoveObject(right_upper_crv, trans)

        # middle1
        trans = (x_m + y_m, 4.5 * y_m, 0)
        rs.MoveObject(left_middle_crv1, trans)

        trans = (x_m + 2.5 * y_m, 4.5 * y_m, 0)
        rs.MoveObject(right_middle_crv1, trans)

        # middle2
        trans = (x_m + y_m, 3 * y_m, 0)
        rs.MoveObject(left_middle_crv2, trans)

        trans = (x_m + 2.5 * y_m, 3 * y_m, 0)
        rs.MoveObject(right_middle_crv2, trans)

        # middle3
        trans = (x_m + y_m, 1.5 * y_m, 0)
        rs.MoveObject(left_middle_crv3, trans)

        trans = (x_m + 2.5 * y_m, 1.5 * y_m, 0)
        rs.MoveObject(right_middle_crv3, trans)

        # lower
        trans = (x_m + y_m, 0, 0)
        rs.MoveObject(left_lower_crv, trans)

        trans = (x_m + 2.5 * y_m, 0, 0)
        rs.MoveObject(right_lower_crv, trans)
        pass

    else:
        sys.exit()

def deploy_SHIGUCHI_crvs(KUMIKI_info, crvs1, crvs2):
    """Deploy crvs.
    Receives:
        KUMIKI_info     list    KUMIKI information
                                [m1_info, m2_info, m1_model, m2_model, direction]

        m1_info                 [x_m1, y_m1, z_m, m1_points]
        m2_info                 [x_m2, y_m2, z_m, m2_points]

        crvs1           list    list of guids [upper, middle, lower]
        crvs2           list    ditto
    Returns:
        ---
    """
    """
    1   Get information from list
    """
    m1_info = KUMIKI_info[0]
    x_m1 = m1_info[0]
    y_m1 = m1_info[1]

    abs(x_m1)
    abs(y_m1)

    m2_info = KUMIKI_info[1]
    x_m2 = m2_info[0]
    y_m2 = m2_info[1]

    abs(x_m2)
    abs(y_m2)

    direction = KUMIKI_info[4]

    m1_upper_crv = crvs1[0]
    m1_middle_crv = crvs1[1]
    m1_lower_crv = crvs1[2]

    m2_upper_crv = crvs2[0]
    m2_middle_crv = crvs2[1]
    m2_lower_crv = crvs2[2]

    """
    2   Deploy crvs to user can pick up crv data.
    """
    if direction == 'UpperRight':
        # upper
        trans = (x_m1 + 2 * y_m1, 0, 0)
        rs.MoveObject(m1_upper_crv, trans)

        trans = (x_m1 + 3.5 * y_m1, y_m1 / 2, 0)
        rs.MoveObject(m2_upper_crv, trans)

        # middle
        trans = (x_m1 + 2 * y_m1, 1.5 * y_m2, 0)
        rs.MoveObject(m1_middle_crv, trans)

        trans = (x_m1 + 3.5 * y_m1, 1.5 * y_m2 + y_m1 / 2, 0)
        rs.MoveObject(m2_middle_crv, trans)

        # lower
        trans = (x_m1 + 2 * y_m1, 3 * y_m2, 0)
        rs.MoveObject(m1_lower_crv, trans)

        trans = (x_m1 + 3.5 * y_m1, 3 * y_m2 + y_m1 / 2, 0)
        rs.MoveObject(m2_lower_crv, trans)

    elif direction == 'UpperLeft':
        # upper
        trans = (x_m1 + 2 * y_m1, 0, 0)
        rs.MoveObject(m1_upper_crv, trans)

        trans = (x_m1 + 3.5 * y_m1, y_m1 / 2, 0)
        rs.MoveObject(m2_upper_crv, trans)

        # middle
        trans = (x_m1 + 2 * y_m1, 1.5 * y_m2, 0)
        rs.MoveObject(m1_middle_crv, trans)

        trans = (x_m1 + 3.5 * y_m1, 1.5 * y_m2 + y_m1 / 2, 0)
        rs.MoveObject(m2_middle_crv, trans)

        # lower
        trans = (x_m1 + 2 * y_m1, 3 * y_m2, 0)
        rs.MoveObject(m1_lower_crv, trans)

        trans = (x_m1 + 3.5 * y_m1, 3 * y_m2 + y_m1 / 2, 0)
        rs.MoveObject(m2_lower_crv, trans)

    elif direction == 'LowerRight':
        # upper
        trans = (x_m1 + 2 * y_m1, 0, 0)
        rs.MoveObject(m1_upper_crv, trans)

        trans = (x_m1 + 3.5 * y_m1, -10, 0)
        rs.MoveObject(m2_upper_crv, trans)

        # middle
        trans = (x_m1 + 2 * y_m1, -1.5 * y_m2, 0)
        rs.MoveObject(m1_middle_crv, trans)

        trans = (x_m1 + 3.5 * y_m1, -1.5 * y_m2 - 10, 0)
        rs.MoveObject(m2_middle_crv, trans)

        # lower
        trans = (x_m1 + 2 * y_m1, -3 * y_m2, 0)
        rs.MoveObject(m1_lower_crv, trans)

        trans = (x_m1 + 3.5 * y_m1, -3 * y_m2 - 10, 0)
        rs.MoveObject(m2_lower_crv, trans)

    elif direction == 'LowerLeft':
        # upper
        trans = (x_m1 + 2 * y_m1, 0, 0)
        rs.MoveObject(m1_upper_crv, trans)

        trans = (x_m1 + 3.5 * y_m1, -10, 0)
        rs.MoveObject(m2_upper_crv, trans)

        # middle
        trans = (x_m1 + 2 * y_m1, -1.5 * y_m2, 0)
        rs.MoveObject(m1_middle_crv, trans)

        trans = (x_m1 + 3.5 * y_m1, -1.5 * y_m2 - 10, 0)
        rs.MoveObject(m2_middle_crv, trans)

        # lower
        trans = (x_m1 + 2 * y_m1, -3 * y_m2, 0)
        rs.MoveObject(m1_lower_crv, trans)

        trans = (x_m1 + 3.5 * y_m1, -3 * y_m2 - 10, 0)
        rs.MoveObject(m2_lower_crv, trans)

    else:
        sys.exit()

    pass

# ------------------------------------------------------------------------------
# CODE--------------------------------------------------------------------------
delete_all()
RUN()
