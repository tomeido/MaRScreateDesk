import rhinoscriptsyntax as rs
import math
import clr

def countDeskFunc(k):
    return len(k)

def lenCurveFunc(k):
    return rs.CurveLength(k)

def filterEdges(e):
    return rs.CurveLength(e) > 1

def scaleLine(line, scale):
        midPoint = rs.CurveMidPoint(line)
        plane = rs.PlaneFromNormal(midPoint, rs.VectorUnitize([0.0,0.0,1.0]))
        ret = rs.ScaleObject(line, midPoint, [scale, scale, 0], copy=False)
        return ret

def placeRowOfDesks(s, edges, offsetEdge, offsetDir, desks, deskPoints, deskDirections, deskWidth, deskLength, rowOffset, columns):
        dCount = 0
        deskCount = rs.CurveLength(offsetEdge) / deskLength
        if deskCount >= 2:
                deskPlacements = rs.DivideCurve(offsetEdge, deskCount) #PointsAtEqualSegmentLength PointsAtEqualChordLength
                perpDir = rs.CurveTangent(offsetEdge, 0.5)
                for deskP in deskPlacements:
                        vec1 = rs.VectorScale(offsetDir, deskWidth * 0.5)
                        vec2 = rs.VectorReverse(vec1)
                        vec3 = rs.VectorScale(offsetDir, deskWidth * 1.5)
                        vec4 = rs.VectorReverse(vec3)
                        r1 = rs.MoveObject(deskP, vec1)
                        r2 = rs.MoveObject(deskP, vec2)
                        r3 = rs.MoveObject(deskP, vec3)
                        r4 = rs.MoveObject(deskP, vec4)
                        desk = rs.AddRectangle(rs.PlaneFromFrame(r1, offsetDir, perpDir), deskWidth, deskLength)
                        desk2 = rs.AddRectangle(rs.PlaneFromFrame(r2, offsetDir, perpDir), deskWidth, deskLength)
                        intersects1 = False
                        intersects2 = False
                        for col in columns:
                                if rs.CurveCurveIntersection(col, desk):
                                        intersects1 = True
                                if rs.CurveCurveIntersection(col, desk2):
                                        intersects2 = True
                        for e in edges:
                                if rs.CurveCurveIntersection(e, desk):
                                        intersects1 = True
                                if rs.CurveCurveIntersection(e, desk2):
                                        intersects2 = True

                        if not intersects1 and rs.CurveCurveIntersection(s, desk):
                                desks.append(desk)
                                dCount += 1
                                deskPoints.append(r3)
                                deskDirections.append(rs.VectorCreate(r1, r3))
                        else:
                                desk.Dispose()
                                r3.Dispose()

                        if not intersects2 and rs.CurveCurveIntersection(s, desk2):
                                desks.append(desk2)
                                dCount += 1
                                deskPoints.append(r4)
                                deskDirections.append(rs.VectorCreate(r2, r4))
                        else:
                                desk2.Dispose()
                                r4.Dispose()

                        vec1.Dispose()
                        vec2.Dispose()
                        r1.Dispose()
                        r2.Dispose()
                perpDir.Dispose()
        return dCount


desks = []
deskPoints = []
deskDirections = []
deskCounts = []

if surfaces and allColumns:
        for i in range(len(surfaces)):
                surface = surfaces[i]
                # figure out direction
                deskCount = 0
                desksGroup = []
                deskPointsGroup = []
                deskDirectionsGroup = []
                edges = rs.DuplicateEdgeCurves(surface, True)
                filteredEdges = list(filter(filterEdges, edges))
                edge = max(filteredEdges, key=lenCurveFunc)
                centerPt = rs.EvaluateSurface(surface, 0.5, 0.5)
                midpoint = rs.CurveMidPoint(edge)
                offsetDir0 = rs.VectorCreate(centerPt, midpoint)
                offsetDir1 = rs.CurveCurvature(edge, 0.5)[1]
                offsetDir2 = rs.VectorReverse(offsetDir1)
                offsetDir = offsetDir1
                if rs.VectorAngle(offsetDir0, offsetDir1) > 90:
                        offsetDir = offsetDir2

                j = 0
                while True:
                        offset =  str(j) + ": " + str((rowOffset + deskWidth) + ((rowOffset + (deskWidth*2)) * j))
                        offsetEdge = rs.MoveObject(edge, offsetDir*((rowOffset + deskWidth) + ((rowOffset + (deskWidth*2)) * j)))
                        offsetEdge2 = scaleLine(offsetEdge, 20.0)
                        offsetEdge3 = rs.CurveSurfaceIntersection(offsetEdge2, surface)
                        offsetEdge4 = rs.AddCurve([offsetEdge3[1],offsetEdge3[2]])
                        if offsetEdge4:
                                dCount = placeRowOfDesks(surface, edges, offsetEdge4, offsetDir, desksGroup, deskPointsGroup, deskDirectionsGroup, deskWidth, deskLength, rowOffset, allColumns[i])
                                deskCount += dCount
                        offsetEdge.Dispose()
                        offsetEdge2.Dispose()
                        for e in offsetEdge3:
                                e.Dispose()

                        if not offsetEdge3:
                                break
                        j += 1
                centerPt.Dispose()
                midpoint.Dispose()
                offsetDir.Dispose()
                offsetDir0.Dispose()
                offsetDir1.Dispose()
                offsetDir2.Dispose()
                #pc.Dispose()
                deskCounts.append(deskCount)
                desks.append(desksGroup)
                deskPoints.append(deskPointsGroup)
                deskDirections.append(deskDirectionsGroup)

a = [desks]
b = [deskPoints]
c = [deskDirections]
d = [deskCounts]
