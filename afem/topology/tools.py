from OCC.BOPAlgo import BOPAlgo_BOP, BOPAlgo_COMMON, BOPAlgo_CUT, \
    BOPAlgo_CUT21, BOPAlgo_FUSE, BOPAlgo_MakerVolume, BOPAlgo_SECTION
from OCC.BRep import BRep_Builder, BRep_Tool
from OCC.BRepAdaptor import BRepAdaptor_Curve, \
    BRepAdaptor_Surface
from OCC.BRepAlgo import brepalgo_ConcatenateWireC0
from OCC.BRepAlgoAPI import BRepAlgoAPI_Common, BRepAlgoAPI_Cut, \
    BRepAlgoAPI_Fuse, BRepAlgoAPI_Section
from OCC.BRepBuilderAPI import BRepBuilderAPI_Copy, BRepBuilderAPI_MakeEdge, \
    BRepBuilderAPI_MakeFace, BRepBuilderAPI_MakeVertex, \
    BRepBuilderAPI_MakeWire, BRepBuilderAPI_Sewing
from OCC.BRepCheck import BRepCheck_Analyzer
from OCC.BRepClass3d import brepclass3d
from OCC.BRepExtrema import BRepExtrema_DistShapeShape, BRepExtrema_IsInFace, \
    BRepExtrema_IsOnEdge
from OCC.BRepGProp import brepgprop
from OCC.BRepMesh import BRepMesh_IncrementalMesh
from OCC.BRepOffset import BRepOffset_Pipe, BRepOffset_RectoVerso, \
    BRepOffset_Skin
from OCC.BRepOffsetAPI import BRepOffsetAPI_MakeOffset, \
    BRepOffsetAPI_MakeOffsetShape, BRepOffsetAPI_MakePipeShell, \
    BRepOffsetAPI_NormalProjection
from OCC.BRepPrimAPI import BRepPrimAPI_MakeHalfSpace, BRepPrimAPI_MakePrism
from OCC.BRepTools import BRepTools_WireExplorer, breptools_OuterWire
from OCC.GCPnts import GCPnts_AbscissaPoint, GCPnts_UniformAbscissa
from OCC.GEOMAlgo import GEOMAlgo_Splitter
from OCC.GProp import GProp_GProps
from OCC.GeomAPI import GeomAPI_ProjectPointOnCurve
from OCC.GeomAbs import GeomAbs_Arc, GeomAbs_BSplineCurve, \
    GeomAbs_BSplineSurface, GeomAbs_BezierCurve, GeomAbs_BezierSurface, \
    GeomAbs_Intersection, GeomAbs_Line, GeomAbs_Plane, GeomAbs_Tangent
from OCC.GeomAdaptor import GeomAdaptor_Curve, GeomAdaptor_Surface
from OCC.GeomConvert import GeomConvert_CompCurveToBSplineCurve
from OCC.ShapeAnalysis import ShapeAnalysis_Edge, ShapeAnalysis_FreeBounds, \
    ShapeAnalysis_FreeBounds_ConnectEdgesToWires, ShapeAnalysis_ShapeTolerance
from OCC.ShapeBuild import ShapeBuild_ReShape
from OCC.ShapeFix import ShapeFix_Shape
from OCC.ShapeUpgrade import ShapeUpgrade_ShapeDivideClosed, \
    ShapeUpgrade_ShapeDivideContinuity, ShapeUpgrade_UnifySameDomain
from OCC.TopAbs import TopAbs_COMPOUND, TopAbs_COMPSOLID, TopAbs_EDGE, \
    TopAbs_FACE, TopAbs_REVERSED, TopAbs_SHELL, TopAbs_SOLID, TopAbs_VERTEX, \
    TopAbs_WIRE
from OCC.TopExp import TopExp_Explorer
from OCC.TopTools import Handle_TopTools_HSequenceOfShape, \
    TopTools_HSequenceOfShape
from OCC.TopoDS import TopoDS_CompSolid, TopoDS_Compound, TopoDS_Edge, \
    TopoDS_Face, TopoDS_Shape, TopoDS_Shell, TopoDS_Solid, TopoDS_Vertex, \
    TopoDS_Wire, topods_CompSolid, topods_Compound, topods_Edge, topods_Face, \
    topods_Shell, topods_Solid, topods_Vertex, topods_Wire
from OCC.gp import gp_Pnt

from ..config import Settings
from ..geometry import CheckGeom, CreateGeom
from ..geometry.bounding_box import BBox
from ..geometry.curves import Line
from ..geometry.methods.create import create_nurbs_curve_from_occ, \
    create_nurbs_surface_from_occ
from ..geometry.surfaces import Plane

_brep_tool = BRep_Tool()


class ShapeTools(object):
    """
    Shape tools.
    """

    @staticmethod
    def is_shape(shape):
        """
        Check if shape is a TopoDS_Shape.

        :param shape:

        :return:
        """
        return isinstance(shape, TopoDS_Shape)

    @staticmethod
    def is_solid(shape):
        """
        Check if the shape is a solid.

        :param shape:

        :return: 
        """
        if isinstance(shape, TopoDS_Solid):
            return True
        if isinstance(shape, TopoDS_Shape) and shape.ShapeType() == \
                TopAbs_SOLID:
            return True
        return False

    @staticmethod
    def to_shape(entity):
        """
        Convert the entity (shape or geometry) to a shape.

        :param entity:

        :return:
        """
        if not entity:
            return None

        # Shapes
        if isinstance(entity, TopoDS_Shape):
            if entity.ShapeType() == TopAbs_VERTEX:
                return topods_Vertex(entity)
            elif entity.ShapeType() == TopAbs_EDGE:
                return topods_Edge(entity)
            elif entity.ShapeType() == TopAbs_WIRE:
                return topods_Wire(entity)
            elif entity.ShapeType() == TopAbs_FACE:
                return topods_Face(entity)
            elif entity.ShapeType() == TopAbs_SHELL:
                return topods_Shell(entity)
            elif entity.ShapeType() == TopAbs_SOLID:
                return topods_Solid(entity)
            elif entity.ShapeType() == TopAbs_COMPSOLID:
                return topods_CompSolid(entity)
            elif entity.ShapeType() == TopAbs_COMPOUND:
                return topods_Compound(entity)
            else:
                return None

        # Geometry
        if CheckGeom.is_point_like(entity):
            return ShapeTools.to_vertex(entity)
        if CheckGeom.is_curve_like(entity):
            return ShapeTools.to_edge(entity)
        if CheckGeom.is_surface_like(entity):
            return ShapeTools.to_face(entity)

        return None

    @staticmethod
    def to_vertex(shape):
        """
        Convert a shape to a vertex.

        :param shape:

        :return:
        """
        if isinstance(shape, TopoDS_Vertex):
            return shape

        if isinstance(shape, gp_Pnt):
            return BRepBuilderAPI_MakeVertex(shape).Vertex()

        if CheckGeom.is_point(shape):
            return BRepBuilderAPI_MakeVertex(shape).Vertex()

        if CheckGeom.is_point_like(shape):
            p = CreateGeom.point_by_xyz(*shape)
            return BRepBuilderAPI_MakeVertex(p).Vertex()

        if ShapeTools.is_shape(shape) and shape.ShapeType() == TopAbs_VERTEX:
            return topods_Vertex(shape)

        return None

    @staticmethod
    def to_edge(shape):
        """
        Convert a shape to an edge.

        :param shape:

        :return:
        """
        if isinstance(shape, TopoDS_Edge):
            return shape

        if CheckGeom.is_curve_like(shape):
            return BRepBuilderAPI_MakeEdge(shape.GetHandle()).Edge()

        if ShapeTools.is_shape(shape) and shape.ShapeType() == TopAbs_EDGE:
            return topods_Edge(shape)

        return None

    @staticmethod
    def to_wire(shape):
        """
        Convert a shape to a wire.

        :param shape:

        :return:
        """
        if isinstance(shape, TopoDS_Wire):
            return shape

        if CheckGeom.is_curve_like(shape):
            edge = BRepBuilderAPI_MakeEdge(shape.GetHandle()).Edge()
            return BRepBuilderAPI_MakeWire(edge).Wire()

        if ShapeTools.is_shape(shape) and shape.ShapeType() == TopAbs_WIRE:
            return topods_Wire(shape)

        if ShapeTools.is_shape(shape) and shape.ShapeType() == TopAbs_EDGE:
            return BRepBuilderAPI_MakeWire(shape).Wire()

        return None

    @staticmethod
    def to_face(shape):
        """
        Convert a shape to a face.

        :param shape:
        :return:
        """
        if isinstance(shape, TopoDS_Face):
            return shape

        if CheckGeom.is_surface_like(shape):
            return BRepBuilderAPI_MakeFace(shape.GetHandle(), 0.).Face()

        if ShapeTools.is_shape(shape) and shape.ShapeType() == TopAbs_FACE:
            return topods_Face(shape)

        return None

    @staticmethod
    def to_shell(shape):
        """
        Convert a shape to a shell.

        :param shape:

        :return:
        """
        if isinstance(shape, TopoDS_Shell):
            return shape

        if ShapeTools.is_shape(shape) and shape.ShapeType() == TopAbs_SHELL:
            return topods_Shell(shape)

        if ShapeTools.is_shape(shape) and shape.ShapeType() == TopAbs_FACE:
            shell = TopoDS_Shell()
            builder = BRep_Builder()
            builder.MakeShell(shell)
            builder.Add(shell, shape)
            return shell

        return None

    @staticmethod
    def to_solid(shape):
        """
        Convert a shape to a solid.

        :param shape:

        :return:
        """
        if isinstance(shape, TopoDS_Solid):
            return shape

        if ShapeTools.is_shape(shape) and shape.ShapeType() == TopAbs_SOLID:
            return topods_Solid(shape)

        return None

    @staticmethod
    def to_compsolid(shape):
        """
        Convert a shape to a compsolid.

        :param shape:

        :return:
        """
        if isinstance(shape, TopoDS_CompSolid):
            return shape

        if (ShapeTools.is_shape(shape) and
                    shape.ShapeType() == TopAbs_COMPSOLID):
            return topods_CompSolid(shape)

        return None

    @staticmethod
    def to_compound(shape):
        """
        Convert a shape to a compound.

        :param shape:

        :return:
        """
        if isinstance(shape, TopoDS_Compound):
            return shape

        if ShapeTools.is_shape(shape) and shape.ShapeType() == TopAbs_COMPOUND:
            return topods_Compound(shape)

        return None

    @staticmethod
    def get_vertices(shape, as_compound=False):
        """
        Get vertices from a shape.

        :return:
        """
        if isinstance(shape, TopoDS_Vertex):
            if as_compound:
                return ShapeTools.make_compound([shape])
            return [shape]

        exp = TopExp_Explorer(shape, TopAbs_VERTEX)
        vertices = []
        while exp.More():
            vi = exp.Current()
            vertex = topods_Vertex(vi)
            vertices.append(vertex)
            exp.Next()
        if as_compound:
            return ShapeTools.make_compound(vertices)
        return vertices

    @staticmethod
    def get_edges(shape, as_compound=False, unique=True):
        """
        Get edges from a shape.

        :param shape:
        :param bool unique: Unique edges based on TShape and Location.
        :param as_compound:

        :return:
        """
        if isinstance(shape, TopoDS_Edge):
            if as_compound:
                return ShapeTools.make_compound([shape])
            return [shape]

        exp = TopExp_Explorer(shape, TopAbs_EDGE)
        edges = []
        while exp.More():
            ei = exp.Current()
            edge = topods_Edge(ei)
            if unique:
                is_unique = True
                for e in edges:
                    if e.IsSame(edge):
                        is_unique = False
                        break
                if is_unique:
                    edges.append(edge)
            else:
                edges.append(edge)
            exp.Next()
        if as_compound:
            return ShapeTools.make_compound(edges)
        return edges

    @staticmethod
    def get_wires(shape, as_compound=False):
        """
        Get wires from a shape.

        :return:
        """
        if isinstance(shape, TopoDS_Wire):
            if as_compound:
                return ShapeTools.make_compound([shape])
            return [shape]

        exp = TopExp_Explorer(shape, TopAbs_WIRE)
        wires = []
        while exp.More():
            wi = exp.Current()
            wire = topods_Wire(wi)
            wires.append(wire)
            exp.Next()
        if as_compound:
            return ShapeTools.make_compound(wires)
        return wires

    @staticmethod
    def get_faces(shape, as_compound=False):
        """
        Get faces from a shape.

        :return:
        """
        if isinstance(shape, TopoDS_Face):
            if as_compound:
                return ShapeTools.make_compound([shape])
            return [shape]

        exp = TopExp_Explorer(shape, TopAbs_FACE)
        faces = []
        while exp.More():
            fi = exp.Current()
            face = topods_Face(fi)
            faces.append(face)
            exp.Next()
        if as_compound:
            return ShapeTools.make_compound(faces)
        return faces

    @staticmethod
    def get_shells(shape, as_compound=False):
        """
        Get shells from a shape.

        :return:
        """
        if isinstance(shape, TopoDS_Shell):
            if as_compound:
                return ShapeTools.make_compound([shape])
            return [shape]

        exp = TopExp_Explorer(shape, TopAbs_SHELL)
        shells = []
        while exp.More():
            si = exp.Current()
            shell = topods_Shell(si)
            shells.append(shell)
            exp.Next()
        if as_compound:
            return ShapeTools.make_compound(shells)
        return shells

    @staticmethod
    def get_solids(shape, as_compound=False):
        """
        Get solids from a shape.

        :return:
        """
        if isinstance(shape, TopoDS_Solid):
            if as_compound:
                return ShapeTools.make_compound([shape])
            return [shape]

        exp = TopExp_Explorer(shape, TopAbs_SOLID)
        solids = []
        while exp.More():
            si = exp.Current()
            solid = topods_Solid(si)
            solids.append(solid)
            exp.Next()
        if as_compound:
            return ShapeTools.make_compound(solids)
        return solids

    @staticmethod
    def get_compounds(shape, as_compound=False):
        """
        Get compounds from a shape.

        :return:
        """
        if isinstance(shape, TopoDS_Compound):
            if as_compound:
                return ShapeTools.make_compound([shape])
            return [shape]

        exp = TopExp_Explorer(shape, TopAbs_COMPOUND)
        compounds = []
        while exp.More():
            ci = exp.Current()
            compound = topods_Compound(ci)
            compounds.append(compound)
            exp.Next()
        if as_compound:
            return ShapeTools.make_compound(compounds)
        return compounds

    @staticmethod
    def outer_wire(face):
        """
        Get outer wire of face.

        :param face:

        :return:
        """
        face = ShapeTools.to_face(face)
        if not face:
            return None
        return breptools_OuterWire(face)

    @staticmethod
    def outer_shell(solid):
        """
        Get the outer shell of the solid.

        :param solid:

        :return:
        """
        return brepclass3d.OuterShell(solid)

    @staticmethod
    def make_compound(shapes):
        """
        Create a compound from a list of shapes.

        :param shapes:

        :return:
        """
        compound = TopoDS_Compound()
        builder = BRep_Builder()
        builder.MakeCompound(compound)
        for shape in shapes:
            shape = ShapeTools.to_shape(shape)
            if not shape:
                continue
            builder.Add(compound, shape)
        return compound

    @staticmethod
    def curve_of_edge(edge):
        """
        Get the curve of the edge.

        :param edge:

        :return:
        """
        edge = ShapeTools.to_edge(edge)
        if not edge:
            return None
        # crv_data = _brep_tool.Curve(edge)
        # adp_crv = GeomAdaptor_Curve(crv_data[0])
        adp_crv = BRepAdaptor_Curve(edge)
        if adp_crv.GetType() == GeomAbs_Line:
            gp_lin = adp_crv.Line()
            crv = Line(gp_lin)
            return crv
        # elif adp_crv.GetType() in [GeomAbs_BezierCurve,
        # GeomAbs_BSplineCurve]:
        crv = adp_crv.BSpline().GetObject()
        crv = create_nurbs_curve_from_occ(crv)
        return crv
        # return None

    @staticmethod
    def curve_of_wire(wire):
        """
        Get the curve of the wire.
        
        :return: 
        """
        wire = ShapeTools.to_wire(wire)
        if not wire:
            return None
        geom_convert = GeomConvert_CompCurveToBSplineCurve()
        exp = ShapeTools.wire_explorer(wire)
        while exp.More():
            e = topods_Edge(exp.Current())
            exp.Next()
            adp_crv = BRepAdaptor_Curve(e)
            tol = ShapeTools.get_tolerance(e, 1)
            # TODO Handle curves other than BSpline
            if adp_crv.GetType() not in [GeomAbs_BSplineCurve,
                                         GeomAbs_BezierCurve]:
                continue
            geom_convert.Add(adp_crv.BSpline(), tol)
        occ_crv = geom_convert.BSplineCurve().GetObject()
        if not occ_crv:
            return None
        crv = create_nurbs_curve_from_occ(occ_crv)
        return crv
        # adp_crv = BRepAdaptor_CompCurve(wire)
        # if adp_crv.GetType() == GeomAbs_Line:
        #     gp_lin = adp_crv.Line()
        #     crv = Line(gp_lin)
        #     return crv
        # elif adp_crv.GetType() in [GeomAbs_BezierCurve,
        # GeomAbs_BSplineCurve]:
        #     crv = adp_crv.BSpline().GetObject()
        #     crv = create_nurbs_curve_from_occ(crv)
        #     return crv
        # return None

    @staticmethod
    def curve_of_shape(shape):
        """
        Get the curve of the shape if possible.
        
        :param shape: 
        :return: 
        """
        shape = ShapeTools.to_shape(shape)
        if isinstance(shape, TopoDS_Edge):
            return ShapeTools.curve_of_edge(shape)
        elif isinstance(shape, TopoDS_Wire):
            return ShapeTools.curve_of_wire(shape)
        else:
            return None

    @staticmethod
    def surface_of_face(face):
        """
        Get the surface of the face.

        :param face:

        :return:
        """
        hsrf = BRep_Tool.Surface(face)
        adp_srf = GeomAdaptor_Surface(hsrf)
        if adp_srf.GetType() == GeomAbs_Plane:
            gp_pln = adp_srf.Plane()
            return Plane(gp_pln)
        elif adp_srf.GetType() in [GeomAbs_BezierSurface,
                                   GeomAbs_BSplineSurface]:
            occ_srf = adp_srf.BSpline().GetObject()
            return create_nurbs_surface_from_occ(occ_srf)

        return None

    @staticmethod
    def surface_of_shape(shape):
        """
        Get the surface of the largest face in the shape.
        
        :param shape: 
        :return: 
        """
        faces = ShapeTools.get_faces(shape)
        if not faces:
            return None
        f = ShapeTools.largest_face(faces)
        if not f:
            return None
        return ShapeTools.surface_of_face(f)

    @staticmethod
    def sew_faces(faces, tol=None):
        """
        Sew faces to make shell.

        :param faces:
        :param tol:

        :return:
        """
        if tol is None:
            tol = max([ShapeTools.get_tolerance(f) for f in faces])

        shell = TopoDS_Shell()
        builder = BRep_Builder()
        builder.MakeShell(shell)
        for f in faces:
            builder.Add(shell, f)

        if len(faces) == 1:
            return shell

        sew = BRepBuilderAPI_Sewing(tol)
        sew.Load(shell)
        sew.Perform()
        sewn_shape = sew.SewedShape()

        return sewn_shape

    @staticmethod
    def unify_shape(shape, edges=True, faces=True, concat_bsplines=False):
        """
        Attempt to unify a shape.

        :param shape:
        :param edges:
        :param faces:
        :param concat_bsplines:

        :return:
        """
        if not ShapeTools.is_shape(shape):
            return None

        unify = ShapeUpgrade_UnifySameDomain(shape, edges, faces,
                                             concat_bsplines)
        unify.Build()
        return ShapeTools.to_shape(unify.Shape())

    @staticmethod
    def bfuse(shape1, shape2, rtype=''):
        """
        Perform BOP Fuse operation between two shapes.

        :param shape1:
        :param shape2:
        :param str rtype: Type of shape to return from the resulting shape.

        :return:
        """
        shape1 = ShapeTools.to_shape(shape1)
        shape2 = ShapeTools.to_shape(shape2)

        bop = BRepAlgoAPI_Fuse(shape1, shape2)
        if bop.ErrorStatus() != 0:
            return []
        if rtype.lower() in ['b', 'builder']:
            return bop

        shape = bop.Shape()
        if not rtype:
            return shape

        rtype = rtype.lower()
        shape = ShapeTools.to_shape(shape)
        if rtype in ['v', 'vertex']:
            return ShapeTools.get_vertices(shape)
        if rtype in ['e', 'edge']:
            return ShapeTools.get_edges(shape)
        if rtype in ['f', 'face']:
            return ShapeTools.get_faces(shape)
        if rtype in ['s', 'solid']:
            return ShapeTools.get_solids(shape)

        return []

    @staticmethod
    def bcommon(shape1, shape2, rtype=''):
        """
        Perform BOP Common operation between two shapes.

        :param shape1:
        :param shape2:
        :param str rtype: Type of shape to return from the resulting shape.

        :return:
        """
        shape1 = ShapeTools.to_shape(shape1)
        shape2 = ShapeTools.to_shape(shape2)

        bop = BRepAlgoAPI_Common(shape1, shape2)
        if bop.ErrorStatus() != 0:
            return []
        if rtype.lower() in ['b', 'builder']:
            return bop

        shape = bop.Shape()
        if not rtype:
            return shape

        rtype = rtype.lower()
        shape = ShapeTools.to_shape(shape)
        if rtype in ['v', 'vertex']:
            return ShapeTools.get_vertices(shape)
        if rtype in ['e', 'edge']:
            return ShapeTools.get_edges(shape)
        if rtype in ['f', 'face']:
            return ShapeTools.get_faces(shape)
        if rtype in ['s', 'solid']:
            return ShapeTools.get_solids(shape)

        return []

    @staticmethod
    def bsection(shape1, shape2, rtype=''):
        """
        Perform BOP Section operation between two shapes.

        :param shape1:
        :param shape2:
        :param str rtype: Type of shape to return from the resulting shape.

        :return:
        """
        shape1 = ShapeTools.to_shape(shape1)
        shape2 = ShapeTools.to_shape(shape2)

        bop = BRepAlgoAPI_Section(shape1, shape2)
        if bop.ErrorStatus() != 0:
            return []
        if rtype.lower() in ['b', 'builder']:
            return bop

        shape = bop.Shape()
        if not rtype:
            return shape

        rtype = rtype.lower()
        shape = ShapeTools.to_shape(shape)
        if rtype in ['v', 'vertex']:
            return ShapeTools.get_vertices(shape)
        if rtype in ['e', 'edge']:
            return ShapeTools.get_edges(shape)
        if rtype in ['f', 'face']:
            return ShapeTools.get_faces(shape)
        if rtype in ['s', 'solid']:
            return ShapeTools.get_solids(shape)

        return []

    @staticmethod
    def bcut(shape1, shape2, rtype=''):
        """
        Perform BOP Cut operation between two shapes.

        :param shape1:
        :param shape2:
        :param str rtype: Type of shape to return from the resulting shape.

        :return:
        """
        shape1 = ShapeTools.to_shape(shape1)
        shape2 = ShapeTools.to_shape(shape2)

        bop = BRepAlgoAPI_Cut(shape1, shape2)
        if bop.ErrorStatus() != 0:
            return []
        if rtype.lower() in ['b', 'builder']:
            return bop

        shape = bop.Shape()
        if not rtype:
            return shape

        rtype = rtype.lower()
        shape = ShapeTools.to_shape(shape)
        if rtype in ['v', 'vertex']:
            return ShapeTools.get_vertices(shape)
        if rtype in ['e', 'edge']:
            return ShapeTools.get_edges(shape)
        if rtype in ['f', 'face']:
            return ShapeTools.get_faces(shape)
        if rtype in ['s', 'solid']:
            return ShapeTools.get_solids(shape)

        return []

    @staticmethod
    def make_halfspace(shape, pref):
        """
        Create a half-space.

        :param shape:
        :param pref:

        :return:
        """
        shape = ShapeTools.to_shape(shape)
        pref = CheckGeom.to_point(pref)
        if not isinstance(shape, (TopoDS_Face, TopoDS_Shell)):
            # Try getting a face or shell from the shape.
            shapes = ShapeTools.get_shells(shape)
            if not shapes:
                shapes = ShapeTools.get_faces(shape)
                if not shapes:
                    return None
            try:
                shape = ShapeTools.sort_by_mass(shapes)[-1]
            except IndexError:
                return None
        if not CheckGeom.is_point(pref):
            return None

        return BRepPrimAPI_MakeHalfSpace(shape, pref).Solid()

    @staticmethod
    def wire_explorer(wire, face=None):
        """
        Create a wire explorer.

        :param wire:
        :param face:

        :return:
        """
        wire = ShapeTools.to_wire(wire)
        face = ShapeTools.to_face(face)
        if not wire:
            return None

        if not face:
            return BRepTools_WireExplorer(wire)
        else:
            return BRepTools_WireExplorer(wire, face)

    @staticmethod
    def is_seam(edge, face):
        """
        Check to see if the edge is a seam edge on the face.

        :param edge:
        :param face:

        :return:
        """
        return ShapeAnalysis_Edge.IsSeam(edge, face)

    @staticmethod
    def first_vertex(edge):
        """
        Return the first vertex of the edge considering orientation.

        :param edge:

        :return:
        """
        return ShapeAnalysis_Edge().FirstVertex(edge)

    @staticmethod
    def last_vertex(edge):
        """
        Return the last vertex of the edge considering orientation.

        :param edge:

        :return:
        """
        return ShapeAnalysis_Edge().LastVertex(edge)

    @staticmethod
    def vertices(edge):
        """
        Return the first and last vertex of the edge.

        :param edge:

        :return:
        """
        return ShapeTools.first_vertex(edge), ShapeTools.last_vertex(edge)

    @staticmethod
    def same_parameter(edge):
        """
        Returns the SameParameter flag for the edge.

        :param edge:

        :return:
        """
        return BRep_Tool.SameParameter(edge)

    @staticmethod
    def same_range(edge):
        """
        Returns the SameRange flag for the edge.

        :param edge:

        :return:
        """
        return BRep_Tool.SameRange(edge)

    @staticmethod
    def parameter(vertex, edge, face=None):
        """
        Return the parameter of the vertex on the edge.

        :param vertex:
        :param edge:
        :param face:

        :return:
        """
        vertex = ShapeTools.to_vertex(vertex)
        edge = ShapeTools.to_edge(edge)
        face = ShapeTools.to_face(face)
        if not vertex or not edge:
            return None
        if not face:
            return BRep_Tool.Parameter(vertex, edge)
        else:
            return BRep_Tool.Parameter(vertex, edge, face)

    @staticmethod
    def parameters(edge, face=None):
        """
        Return the first and last parameters on the edge.

        :param edge:
        :param face:

        :return:
        """
        v1, v2 = ShapeTools.vertices(edge)
        u1 = ShapeTools.parameter(v1, edge, face)
        u2 = ShapeTools.parameter(v2, edge, face)
        return u1, u2

    @staticmethod
    def is_valid(shape):
        """
        Check the shape for errors.

        :param shape:

        :return:
        """
        shape = ShapeTools.to_shape(shape)
        if not shape:
            return False
        check_shp = BRepCheck_Analyzer(shape, True)
        return check_shp.IsValid()

    @staticmethod
    def fix_shape(shape, max_tol=None):
        """
        Attempt to fix the shape.

        :param shape:
        :param max_tol:

        :return:
        """
        shape = ShapeTools.to_shape(shape)
        if not shape:
            return None
        fix = ShapeFix_Shape(shape)
        if max_tol is not None:
            fix.SetMaxTolerance(max_tol)
        fix.Perform()
        new_shape = fix.Shape()
        return ShapeTools.to_shape(new_shape)

    @staticmethod
    def get_tolerance(shape, mode=0):
        """
        Compute the global tolerance of the shape.

        :param shape:
        :param mode: Average (0), maximal (1), minimal (2)

        :return:
        """
        tol = ShapeAnalysis_ShapeTolerance()
        tol.AddTolerance(shape)
        return tol.GlobalTolerance(mode)

    @staticmethod
    def points_along_edge(edge, dx):
        """
        Create points along an edge.

        :param edge:
        :param dx:

        :return:
        """
        edge = ShapeTools.to_edge(edge)
        if not edge:
            return []

        # Calculate number of points.
        adp_crv = BRepAdaptor_Curve(edge)
        arc_len = GCPnts_AbscissaPoint.Length(adp_crv,
                                              adp_crv.FirstParameter(),
                                              adp_crv.LastParameter(),
                                              Settings.gtol)
        nb_pts = int(arc_len / dx) + 1

        pac = GCPnts_UniformAbscissa(adp_crv, nb_pts, Settings.gtol)
        if not pac.IsDone():
            return []

        pnts = []
        for i in range(1, pac.NbPoints() + 1):
            u = pac.Parameter(i)
            gp_pnt = adp_crv.Value(u)
            pnts.append(CreateGeom.point_by_xyz(gp_pnt.X(), gp_pnt.Y(),
                                                gp_pnt.Z()))

        if edge.Orientation() == TopAbs_REVERSED:
            pnts.reverse()

        return pnts

    @staticmethod
    def linear_properties(shape):
        """
        Calculate linear properties of a shape.

        :param shape:

        :return:
        """
        shape = ShapeTools.to_shape(shape)
        if not shape:
            return None

        props = GProp_GProps()
        brepgprop.LinearProperties(shape, props)
        return props

    @staticmethod
    def surface_properties(shape):
        """
        Calculate surface properties of a shape.

        :param shape:

        :return:
        """
        shape = ShapeTools.to_shape(shape)
        if not shape:
            return None

        props = GProp_GProps()
        brepgprop.SurfaceProperties(shape, props, Settings.gtol)
        return props

    @staticmethod
    def volume_properties(shape):
        """
        Calculate volume properties of a shape.

        :param shape:

        :return:
        """
        shape = ShapeTools.to_shape(shape)
        if not shape:
            return None

        props = GProp_GProps()
        brepgprop.VolumeProperties(shape, props)
        return props

    @staticmethod
    def shape_mass(shape):
        """
        Calculate the mass of a shape.

        :param shape:

        :return:
        """
        shape = ShapeTools.to_shape(shape)
        if not shape:
            return None

        shape_type = shape.ShapeType()
        if shape_type >= TopAbs_WIRE:
            props = ShapeTools.linear_properties(shape)
        elif TopAbs_SHELL <= shape_type <= TopAbs_FACE:
            props = ShapeTools.surface_properties(shape)
        else:
            props = ShapeTools.volume_properties(shape)

        return props.Mass()

    @staticmethod
    def center_of_mass(shape):
        """
        Calculate center of mass of shape.

        :param shape:

        :return:
        """
        shape = ShapeTools.to_shape(shape)
        if not shape:
            return None

        shape_type = shape.ShapeType()
        if shape_type >= TopAbs_WIRE:
            props = ShapeTools.linear_properties(shape)
        elif TopAbs_SHELL <= shape_type <= TopAbs_FACE:
            props = ShapeTools.surface_properties(shape)
        else:
            props = ShapeTools.volume_properties(shape)

        cg = props.CentreOfMass()
        return CreateGeom.point_by_xyz(cg.X(), cg.Y(), cg.Z())

    @staticmethod
    def box_from_plane(pln, width, height, depth):
        """
        Create a solid box from a plane.

        :param pln:
        :param width:
        :param height:
        :param depth:

        :return:
        """
        if not CheckGeom.is_plane(pln):
            return None

        # Make finite face from plane.
        w = width / 2.
        h = height / 2.
        gp_pln = pln.Pln()
        face = BRepBuilderAPI_MakeFace(gp_pln, -w, w, -h, h).Face()

        # Get normal vector at center of plane and use depth to extrude.
        vn = pln.norm(0., 0.)
        vn.Normalize()
        vn.Scale(depth)
        shape = BRepPrimAPI_MakePrism(face, vn).Shape()
        return shape

    @staticmethod
    def bop_algo(args, tools, operation='fuse'):
        """
        Perform BOP using BOPAlgo_BOP tool.

        :param args:
        :param tools:
        :param operation:

        :return:
        """
        bop = BOPAlgo_BOP()

        for shape in args:
            shape = ShapeTools.to_shape(shape)
            bop.AddArgument(shape)
        for shape in tools:
            shape = ShapeTools.to_shape(shape)
            bop.AddTool(shape)

        try:
            operation = operation.lower()
        except AttributeError:
            return None
        if operation in ['fuse']:
            operation = BOPAlgo_FUSE
        elif operation in ['common']:
            operation = BOPAlgo_COMMON
        elif operation in ['cut']:
            operation = BOPAlgo_CUT
        elif operation in ['cut21']:
            operation = BOPAlgo_CUT21
        elif operation in ['section', 'intersect']:
            operation = BOPAlgo_SECTION
        else:
            return None

        bop.SetOperation(operation)
        bop.Perform()
        if bop.ErrorStatus() != 0:
            return None
        return bop.Shape()

    @staticmethod
    def connect_edges(edges, tol=None, shared=False):
        """
        Build wires from a list of unsorted edges.

        :param edges:
        :param tol:
        :param shared:

        :return:
        """
        hedges = TopTools_HSequenceOfShape()
        for e in edges:
            hedges.Append(e)

        if tol is None:
            tol = max([ShapeTools.get_tolerance(e) for e in edges])

        # noinspection PyArgumentList
        hwires = Handle_TopTools_HSequenceOfShape()
        ShapeAnalysis_FreeBounds_ConnectEdgesToWires(hedges.GetHandle(),
                                                     tol, shared, hwires)

        wires_obj = hwires.GetObject()
        wires = []
        for i in range(1, wires_obj.Length() + 1):
            w = topods_Wire(wires_obj.Value(i))
            wires.append(w)

        return wires

    @staticmethod
    def make_prism(shape, vec):
        """
        Make a linear swept topology (i.e., prism).

        :param shape:
        :param vec:

        :return:
        """
        shape = ShapeTools.to_shape(shape)
        vec = CheckGeom.to_vector(vec)
        return BRepPrimAPI_MakePrism(shape, vec).Shape()

    @staticmethod
    def concatenate_wire(wire):
        """
        Create an edge by joining all the edges of the wire. The edge may
        have C0 continuity.

        :param wire:
        :return:
        """
        wire = ShapeTools.to_wire(wire)
        if not wire:
            return None
        return brepalgo_ConcatenateWireC0(wire)

    @staticmethod
    def incremental_mesh(shape, linear, is_relative=False, angular=0.5):
        """
        Builds the mesh of a shape.

        :param shape:
        :param linear:
        :param is_relative:
        :param angular:

        :return:
        """
        BRepMesh_IncrementalMesh(shape, linear, is_relative, angular, False)

    @staticmethod
    def plane_from_section(shape1, shape2, pref):
        """
        Create plane from intersection of two shapes.
        """
        # Intersect the two shapes.
        edges = ShapeTools.bsection(shape1, shape2, 'edge')
        if not edges:
            return None

        # Tessellate the edges.
        for e in edges:
            ShapeTools.incremental_mesh(e, 1., True)

        # Gather points to fit a plane.
        pnts = [pref]
        for e in edges:
            hpoly = BRep_Tool().Polygon3D(e, e.Location())
            tcol_pnts = hpoly.GetObject().Nodes()
            for i in range(1, tcol_pnts.Length() + 1):
                gp_pnt = tcol_pnts.Value(i)
                pnt = CheckGeom.to_point(gp_pnt)
                pnts.append(pnt)
        if len(pnts) < 3:
            return None

        return CreateGeom.fit_plane(pnts)

    @staticmethod
    def points_along_shape(shape, maxd=None, npts=None, u1=None, u2=None,
                           s1=None, s2=None, shape1=None, shape2=None):
        """
        Create points along an edge, wire, or curve.

        :param shape:
        :param maxd:
        :param npts:
        :param u1:
        :param u2:
        :param s1:
        :param s2:
        :param shape1:
        :param shape2:

        :return:
        """
        # Get adaptor curve.
        if CheckGeom.is_curve_like(shape):
            adp_crv = GeomAdaptor_Curve(shape.GetHandle())
            edge = BRepBuilderAPI_MakeEdge(shape.GetHandle()).Edge()
        elif isinstance(shape, TopoDS_Shape):
            if shape.ShapeType() == TopAbs_EDGE:
                edge = shape
                adp_crv = BRepAdaptor_Curve(edge)
            elif shape.ShapeType() == TopAbs_WIRE:
                edge = brepalgo_ConcatenateWireC0(shape)
                adp_crv = BRepAdaptor_Curve(edge)
            else:
                return []
        else:
            return []

        # Check parameters.
        if u1 is None:
            u1 = adp_crv.FirstParameter()
        if u2 is None:
            u2 = adp_crv.LastParameter()
        if u1 > u2:
            u1, u2 = u2, u1

        # Adjust parameter if shapes are provided.
        if isinstance(shape1, TopoDS_Shape):
            verts = ShapeTools.bsection(edge, shape1, 'vertex')
            prms = []
            for v in verts:
                gp_pnt = BRep_Tool.Pnt(v)
                proj = GeomAPI_ProjectPointOnCurve(gp_pnt, adp_crv.Curve())
                if proj.NbPoints() < 1:
                    continue
                umin = proj.LowerDistanceParameter()
                prms.append(umin)
            u1 = min(prms)
        if isinstance(shape2, TopoDS_Shape):
            verts = ShapeTools.bsection(edge, shape2, 'vertex')
            prms = []
            for v in verts:
                gp_pnt = BRep_Tool.Pnt(v)
                proj = GeomAPI_ProjectPointOnCurve(gp_pnt, adp_crv.Curve())
                if proj.NbPoints() < 1:
                    continue
                umin = proj.LowerDistanceParameter()
                prms.append(umin)
            u2 = max(prms)

        # Adjust u1 and u2 is s1 and s2 are provided.
        if s1 is not None:
            pac = GCPnts_AbscissaPoint(Settings.gtol, adp_crv, s1, u1)
            if pac.IsDone():
                u1 = pac.Parameter()
        if s2 is not None:
            pac = GCPnts_AbscissaPoint(Settings.gtol, adp_crv, s2, u2)
            if pac.IsDone():
                u2 = pac.Parameter()

        # Adjust step size if necessary.
        if maxd is not None:
            arc_len = GCPnts_AbscissaPoint.Length(adp_crv, u1, u2,
                                                  Settings.gtol)
            nb_pts = int(arc_len / maxd) + 1
        else:
            nb_pts = int(npts)

        # Minimum number of points if maxd and npts are provided.
        if maxd is not None and npts is not None:
            if nb_pts < npts:
                nb_pts = int(npts)

        if nb_pts < 1:
            return []

        # OCC uniform abscissa.
        occ_pnts = GCPnts_UniformAbscissa(adp_crv, nb_pts, u1, u2,
                                          Settings.gtol)
        if not occ_pnts.IsDone():
            return []

        # Gather results.
        npts = occ_pnts.NbPoints()
        points = []
        for i in range(1, npts + 1):
            u = occ_pnts.Parameter(i)
            gp_pnt = adp_crv.Value(u)
            pnt = CheckGeom.to_point(gp_pnt)
            points.append(pnt)

        return points

    @staticmethod
    def divide_closed(shape):
        """
        Divide a closed shape.

        :param shape:

        :return:
        """
        shape = ShapeTools.to_shape(shape)
        if not shape:
            return None

        div = ShapeUpgrade_ShapeDivideClosed(shape)
        div.Perform()
        return ShapeTools.to_shape(div.Result())

    @staticmethod
    def divide_c0(shape):
        """
        Divide a shape at C0 boundaries.

        :param shape:

        :return:
        """
        shape = ShapeTools.to_shape(shape)
        if not shape:
            return None

        div = ShapeUpgrade_ShapeDivideContinuity(shape)
        div.Perform()
        return ShapeTools.to_shape(div.Result())

    @staticmethod
    def get_free_edges(shape, as_compound=False):
        """
        Get the free edges of a shape.

        :param shape:
        :param bool as_compound:

        :return:
        """
        faces = ShapeTools.get_faces(shape)
        if not shape:
            return []

        compound = ShapeTools.make_compound(faces)
        tol = ShapeTools.get_tolerance(compound, 1)
        fb_tool = ShapeAnalysis_FreeBounds(compound, tol)
        closed_edges = ShapeTools.get_edges(fb_tool.GetClosedWires())
        open_edges = ShapeTools.get_edges(fb_tool.GetOpenWires())
        edges = closed_edges + open_edges
        if as_compound:
            return ShapeTools.make_compound(edges)
        return edges

    @staticmethod
    def face_from_plane(pln, umin, umax, vmin, vmax):
        """
        Create a finite face from a plane.
        
        :param pln: 
        :param umin: 
        :param umax: 
        :param vmin: 
        :param vmax: 
        
        :return: 
        """
        if not CheckGeom.is_plane(pln):
            return None
        builder = BRepBuilderAPI_MakeFace(pln.Pln(), umin, umax, vmin, vmax)
        if not builder.IsDone():
            return None
        return builder.Face()

    @staticmethod
    def wires_from_shape(shape):
        """
        Use edges from the shape to create connected wires.
        
        :param shape:
         
        :return: 
        """
        edges = ShapeTools.get_edges(shape)
        if not edges:
            return []

        return ShapeTools.connect_edges(edges)

    @staticmethod
    def shape_length(shape):
        """
        Calculate the length of the shape.
        
        :param shape: 
        
        :return: 
        """
        shape = ShapeTools.to_shape(shape)
        if not shape:
            return None

        props = ShapeTools.linear_properties(shape)
        return props.Mass()

    @staticmethod
    def shape_area(shape):
        """
        Calculate the area of the shape.

        :param shape: 

        :return: 
        """
        shape = ShapeTools.to_shape(shape)
        if not shape:
            return None

        props = ShapeTools.surface_properties(shape)
        return props.Mass()

    @staticmethod
    def shape_volume(shape):
        """
        Calculate the volume of the shape.

        :param shape: 

        :return: 
        """
        shape = ShapeTools.to_shape(shape)
        if not shape:
            return None

        props = ShapeTools.volume_properties(shape)
        return props.Mass()

    @staticmethod
    def sort_by_mass(shapes):
        """
        Sort shapes by mass.

        :param shapes:

        :return: 
        """
        if len(shapes) == 1:
            return shapes
        shape_data = []
        for shape in shapes:
            mass = ShapeTools.shape_mass(shape)
            if mass:
                shape_data.append((mass, shape))
        if not shape_data:
            return []
        shape_data.sort(key=lambda tup: tup[0])
        return [data[1] for data in shape_data]

    @staticmethod
    def longest_wire(wires):
        """
        Get the longest wire.
        
        :param wires:
         
        :return: 
        """
        try:
            return ShapeTools.sort_by_mass(wires)[-1]
        except IndexError:
            return None

    @staticmethod
    def shortest_wire(wires):
        """
        Get the shortest wire.

        :param wires:

        :return: 
        """
        try:
            return ShapeTools.sort_by_mass(wires)[0]
        except IndexError:
            return None

    @staticmethod
    def largest_face(faces):
        """
        Get the largest face.
        
        :param faces:
         
        :return: 
        """
        try:
            return ShapeTools.sort_by_mass(faces)[-1]
        except IndexError:
            return None

    @staticmethod
    def smallest_face(faces):
        """
        Get the smallest face.

        :param faces:

        :return: 
        """
        try:
            return ShapeTools.sort_by_mass(faces)[0]
        except IndexError:
            return None

    @staticmethod
    def bounding_box(shape):
        """
        Create a bounding box from the shape.
        
        :param shape:
         
        :return: 
        """
        shape = ShapeTools.to_shape(shape)
        if not shape:
            return None

        if shape.IsNull():
            return None

        bbox = BBox()
        bbox.add_shape(shape)
        return bbox

    @staticmethod
    def copy_shape(shape, copy_geom=True):
        """
        Copy a shape.
        
        :param shape: 
        :param copy_geom: 
         
        :return: 
        """
        copy = BRepBuilderAPI_Copy(shape, copy_geom)
        if not copy.IsDone():
            return None
        return copy.Shape()

    @staticmethod
    def offset_wire(spine, distance, altitude=0., join=GeomAbs_Arc,
                    is_open=False):
        """
        Offset wire in a planar face.
        
        :param spine: 
        :param distance: 
        :param altitude: 
        :param join: 
        :param is_open: 
        
        :return: 
        """
        spine = ShapeTools.to_shape(spine)
        if not isinstance(spine, (TopoDS_Wire, TopoDS_Face)):
            return None

        if join < GeomAbs_Arc:
            join = GeomAbs_Arc
        if join > GeomAbs_Intersection:
            join = GeomAbs_Intersection
        if join not in [GeomAbs_Arc, GeomAbs_Tangent, GeomAbs_Intersection]:
            return None

        offset = BRepOffsetAPI_MakeOffset(spine, join, is_open)
        offset.Perform(distance, altitude)
        if not offset.IsDone():
            return None

        return ShapeTools.to_shape(offset.Shape())

    @staticmethod
    def offset_shape(shape, distance, tol, mode=BRepOffset_Skin,
                     intersection=False, self_intersect=False,
                     join=GeomAbs_Arc):
        """
        Offset a shape to build a shell.
        
        :param shape: 
        :param distance: 
        :param tol: 
        :param mode: 
        :param intersection: 
        :param self_intersect: 
        :param join: 
        
        :return: 
        """
        shape = ShapeTools.to_shape(shape)
        if not shape:
            return None

        if join < GeomAbs_Arc:
            join = GeomAbs_Arc
        if join > GeomAbs_Intersection:
            join = GeomAbs_Intersection
        if join not in [GeomAbs_Arc, GeomAbs_Tangent, GeomAbs_Intersection]:
            return None

        if mode < BRepOffset_Skin:
            mode = BRepOffset_Skin
        if mode > BRepOffset_RectoVerso:
            mode = BRepOffset_RectoVerso
        if mode not in [BRepOffset_Skin, BRepOffset_Pipe,
                        BRepOffset_RectoVerso]:
            return None

        offset = BRepOffsetAPI_MakeOffsetShape(shape, distance, tol, mode,
                                               intersection, self_intersect,
                                               join)
        if not offset.IsDone():
            return None

        return ShapeTools.to_shape(offset.Shape())

    @staticmethod
    def make_pipe_shell(spine, profiles, spine_support,
                        with_contact=False, with_correction=False):
        """
        Create a shell by sweeping profile(s) along a spine with a normal set
        by a shape.
        
        :param spine: 
        :param profiles: 
        :param spine_support:
        :param with_contact:
        :param with_correction:
         
        :return: 
        """
        spine = ShapeTools.to_wire(spine)
        spine_support = ShapeTools.to_shape(spine_support)
        if not spine or not spine_support:
            return None

        builder = BRepOffsetAPI_MakePipeShell(spine)
        builder.SetMode(spine_support)
        for profile in profiles:
            profile = ShapeTools.to_shape(profile)
            if not profile:
                continue
            builder.Add(profile, with_contact, with_correction)
        if not builder.IsReady():
            return None
        builder.Build()
        if not builder.IsDone():
            return None
        return ShapeTools.to_shape(builder.Shape())

    @staticmethod
    def shape_normal_vector(pnt, shape):
        """
        Calculate the normal of a shape at a point.
        
        :param pnt: 
        :param shape: 
        
        :return: 
        """
        pnt = CheckGeom.to_point(pnt)
        shape = ShapeTools.to_shape(shape)
        if not pnt or not shape:
            return None, None

        v = ShapeTools.to_vertex(pnt)
        dist = BRepExtrema_DistShapeShape(shape, v)
        if not dist.IsDone():
            return None, None

        if dist.SupportTypeShape1(1) == BRepExtrema_IsInFace:
            u, v = dist.ParOnFaceS1(1)
            f = dist.SupportOnShape1(1)
            f = ShapeTools.to_face(f)
            adp_srf = BRepAdaptor_Surface(f)
            p = CreateGeom.point()
            adp_srf.D0(u, v, p)
            vu = adp_srf.DN(u, v, 1, 0)
            vv = adp_srf.DN(u, v, 0, 1)
            vn = vu.Crossed(vv)
            vn.Normalize()
            vn = CheckGeom.to_vector(vn)
            return p, vn
        elif dist.SupportTypeShape1(1) == BRepExtrema_IsOnEdge:
            # TODO What if normal is on edge?
            pass
        return None, None

    @staticmethod
    def shape_normal_profile(pnt, shape, height):
        """
        Create a profile normal to the shape at a point.
        
        :param pnt: 
        :param shape: 
        :param height: 
        
        :return: 
        """
        p0, vn = ShapeTools.shape_normal_vector(pnt, shape)
        if not p0 or not vn:
            return None

        vn.Scale(height)
        p1 = CreateGeom.copy_geom(p0)
        p1.Translate(vn)
        e = BRepBuilderAPI_MakeEdge(p0, p1).Edge()
        w = BRepBuilderAPI_MakeWire(e).Wire()
        return w

    @staticmethod
    def min_distance(shape1, shape2):
        """
        Find the minimum distance between two shapes.
        
        :param shape1: 
        :param shape2: 
        :return: 
        """
        shape1 = ShapeTools.to_shape(shape1)
        shape2 = ShapeTools.to_shape(shape2)
        if not shape1 or not shape2:
            return None, None, None

        dist = BRepExtrema_DistShapeShape(shape1, shape2)
        if not dist.IsDone():
            return None, None, None

        dmin = dist.Value()
        p1 = dist.PointOnShape1(1)
        p2 = dist.PointOnShape2(1)
        p1 = CheckGeom.to_point(p1)
        p2 = CheckGeom.to_point(p2)
        return dmin, p1, p2

    @staticmethod
    def normal_projection(basis_shape, to_project):
        """
        Perform the normal projection of a shape.
        
        :param basis_shape: 
        :param to_project: 
        :return: 
        """
        basis_shape = ShapeTools.to_shape(basis_shape)
        to_project = ShapeTools.to_shape(to_project)
        if not basis_shape or not to_project:
            return []

        proj = BRepOffsetAPI_NormalProjection(basis_shape)
        proj.Add(to_project)
        proj.Build()
        if not proj.IsDone():
            return []

        shape = proj.Shape()
        return ShapeTools.get_wires(shape)

    @staticmethod
    def adjacent_faces(edge, shape):
        """
        Get all the faces of the shape that are adjacent to the edge.
        
        :param edge: 
        :param shape:
         
        :return: 
        """
        edge = ShapeTools.to_edge(edge)
        shape = ShapeTools.to_shape(shape)
        if not edge or not shape:
            return []

        adj_faces = []
        for face in ShapeTools.get_faces(shape):
            for e in ShapeTools.get_edges(face):
                if edge.IsSame(e):
                    adj_faces.append(face)
                    break
        return adj_faces

    @staticmethod
    def split_wire(wire, splitter):
        """
        Split a wire with a shape and update.
        
        :param wire: 
        :param splitter: 
        
        :return: 
        """
        wire = ShapeTools.to_wire(wire)
        splitter = ShapeTools.to_shape(splitter)
        if not wire or not splitter:
            return None

        # Split algorithm
        bop = GEOMAlgo_Splitter()
        bop.AddArgument(wire)
        bop.AddTool(splitter)
        bop.Perform()
        if bop.ErrorStatus() != 0:
            return None

        # Replace edges in wire.
        reshape = ShapeBuild_ReShape()
        performed = False
        for old_edge in ShapeTools.get_edges(wire):
            # Check deleted.
            if bop.IsDeleted(old_edge):
                reshape.Remove(old_edge)
                performed = True
                break

            # Check modified
            modified = bop.Modified(old_edge)
            if modified.IsEmpty():
                continue

            # Put modified edges into compound.
            new_edges = []
            while not modified.IsEmpty():
                shape = modified.First()
                new_edges.append(shape)
                modified.RemoveFirst()
            if not new_edges:
                continue

            # Replace old edge with new.
            new_edges = ShapeTools.make_compound(new_edges)
            reshape.Replace(old_edge, new_edges)
            performed = True

        # Apply substitution.
        if not performed:
            return wire
        new_wire = reshape.Apply(wire)
        return ShapeTools.to_wire(new_wire)

    @staticmethod
    def nearest_shape(shape, others):
        """
        Find the nearest shape to a given shape.

        :param shape:
        :param others:
        :return:
        """
        if not others:
            return None
        if len(others) == 1:
            return others[0]
        shape = ShapeTools.to_shape(shape)
        if not shape:
            return None

        smin = others[0]
        dmin = ShapeTools.min_distance(shape, smin)
        for s in others[1:]:
            di = ShapeTools.min_distance(shape, s)
            if di < dmin:
                dmin = di
                smin = s
        return smin

    @staticmethod
    def make_volume(shapes, intersect=False):
        """
        Make volume(s) from a list of shapes.

        :param list shapes: List of shapes to create volume(s).
        :param bool intersect: Option to first intersect the shapes.

        :return: Volume(s) created from list of shapes. If a single volume
            is created, a solid will be returned. If more than one
            volume was created, a compound will be returned containing all
            the solids. If nothing is created *None* will be returned.
        :rtype: TopoDS_Shape or None
        """
        bop = BOPAlgo_MakerVolume()
        for shape in shapes:
            shape = ShapeTools.to_shape(shape)
            if not shape:
                continue
            bop.AddArgument(shape)
        bop.SetIntersect(intersect)
        bop.Perform()

        if bop.ErrorStatus() != 0:
            return None

        return bop.Shape()

    @staticmethod
    def surface_center_of_mass(shape):
        """
        Calculate the surface center of mass of a shape.

        :param shape:

        :return:
        """
        props = ShapeTools.surface_properties(shape)
        if not props:
            return None

        return props.CentreOfMass()

    @staticmethod
    def linear_center_of_mass(shape):
        """
        Calculate the linear center of mass of a shape.

        :param shape:

        :return:
        """
        props = ShapeTools.linear_properties(shape)
        if not props:
            return None

        return props.CentreOfMass()
