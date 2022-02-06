# import sys
# reload(sys)
# sys.setdefaultencoding('utf-8')

"""
    module is for creating graph connector data base and populating with the relevent
    data for analysis
"""
import json
import logging
import logging.handlers
from string import Template

import py2neo
from py2neo import Graph, Node, Relationship


class GraphConnector(object):
    """
    Neo4j Insertion Client
    """

    def __init__(
        self, url="http://neo4j:root@192.168.100.151:7474/db/data/", log_file="twitter"
    ):
        self.logger = logging.getLogger(log_file + ".GraphConnector")
        self.logger.info("creating an instance of GraphConnector")

        self.graph = Graph(url)
        # self.create_uniqueness_constraint("Target", "id")
        # self.create_uniqueness_constraint("Friend", "id")

    def create_uniqueness_constraint(self, label, property_key):
        """Create a uniqueness constraint for a label."""
        if len(self.graph.schema.get_uniqueness_constraints(label)) == 0:
            self.graph.schema.create_uniqueness_constraint(label, property_key)
        self.logger.info(
            "Creating Constraints with Lable: %s on %s", label, property_key
        )

    def rep_handler(self, userid, f_node, p_tag):
        userid = int(userid)
        replicate = """
        match(n:Friend) where n.id={fid}
        call apoc.refactor.cloneNodesWithRelationships([n]) yield input, output, error
        set output.uid={userid}
        remove output:Friend
        set output:Target
        return output, n, error
        """
        if p_tag == "Target":
            replicate = """
        match(n:Target) where n.id={fid}
        call apoc.refactor.cloneNodesWithRelationships([n]) yield input, output, error
        set output.uid={userid}
        return output, n, error
        """

        output = None
        inputt = None
        # try:
        inout = self.graph.run(
            replicate, parameters={"fid": f_node["id"], "userid": userid, "ptag": p_tag}
        )
        # print inout.data()
        # print inout, type(inout)
        # print dir(inout)
        if inout.forward() > 0:
            output, inputt, error = inout.current()
        else:
            print("Query failed f_id" + f_node["id"] + "userid " + userid)
            return None
        # output, inputt, error = inout.current()

        print("output", output)
        print("input", inputt)
        print("error", error)
        if error is None:
            remove_rel = """
            match (other_ts:Target) where other_ts.uid<>{uid} with collect(other_ts) as others
            match (users_target:Target)-[r1]->(output:Target) where users_target in others and output.uid ={uid} 
            and output.id = {new_tid}  delete r1
            """
            print("removing relations")
            try:
                self.graph.run(
                    remove_rel,
                    parameters={"uid": output["uid"], "new_tid": output["id"]},
                )
            except Exception as identifier:
                print("error in remove first", identifier)
                return

            if p_tag == "Target":
                return output

            remove_rel_from_target = """
            match (target:Target)-[r2]->(input:Friend) where target.uid = {uid} and input.id= {fid}  delete r2
            """
            print("removing relations 2")

            try:
                self.graph.run(
                    remove_rel_from_target,
                    parameters={"uid": output["uid"], "fid": inputt["id"]},
                )
                return output
            except Exception as identifier:
                print("error in second", identifier)
                return

        else:
            print("replication failed XXXXXXX")
            print(error)
            return None

    def create_target_nodes(
        self,
        t_id,
        t_id_numeric,
        t_name,
        t_link,
        t_type,
        t_status_count,
        t_friend_count,
        t_follower_count,
        t_location,
        t_profile_pic_link,
        userid,
        tags="",
        created_at="",
        case_number="",
        reference_number="",
        edu="",
        work="",
        city="",
    ):

        tnode = self.find_user_target(t_id_numeric, userid)
        if tnode is not None:
            self.logger.info("node already exists --initiaL numeric id")
            if tnode["n"]["reference_number"]:
                reference_number_list = tnode["n"]["reference_number"].split(",") + [
                    reference_number
                ]
                reference_number_set = set(reference_number_list)
                reference_number = reference_number_set.difference(set(["", " "]))
                reference_number = ",".join(reference_number)

            if tnode["n"]["case_number"]:
                case_number_list = tnode["n"]["case_number"].split(",") + [case_number]
                case_number_set = set(case_number_list)
                case_number = case_number_set.difference(set(["", " "]))
                case_number = ",".join(case_number)
            tnode["n"]["numaric_id"] = t_id_numeric
            tnode["n"]["reference_number"] = reference_number
            tnode["n"]["case_number"] = case_number
            tnode["n"]["creted_at"] = created_at
            tnode["n"]["picture_link"] = t_profile_pic_link
            tnode["n"].push()

            return tnode

        tnode = self.find_user_target(t_id, userid)
        if tnode is None:

            fnode = self.graph.run(
                "Match (n:Friend  {id:'" + t_id + "',uid:" + str(userid) + "}) return n"
            )
            fnode = fnode.data()
            if not fnode:
                #### Numeric ID check base (Checking in Id attribute )####
                tnode = self.find_user_target(t_id_numeric, userid)
                if tnode is None:
                    fnode = self.graph.run(
                        "Match (n:Friend  {id:'"
                        + t_id_numeric
                        + "',uid:"
                        + str(userid)
                        + "}) return n"
                    )
                    fnode = fnode.data()
                    if not fnode:
                        ### Check if t_id_numeric is in numaric_id attribute of Friend Node ###
                        tnode = self.find_user_target_numeric(t_id_numeric, userid)
                        if tnode is None:

                            tnode = Node(
                                "Target",
                                id=str(t_id_numeric),
                                numaric_id=t_id_numeric,
                                name=t_name,
                                edu=edu,
                                work=work,
                                city=city,
                                profile=t_link,
                                type=t_type,
                                status_count=t_status_count,
                                friend_count=t_friend_count,
                                follower_count=t_follower_count,
                                location=t_location,
                                picture_link=t_profile_pic_link,
                                uid=int(userid),
                                tags=tags,
                                created_at=created_at,
                                case_number=case_number,
                                reference_number=reference_number,
                            )
                            self.logger.info("Creating new node")
                            self.graph.merge(tnode)
                            self.logger.info(
                                "Target Record inserted with values %s", t_id_numeric
                            )

                        else:
                            self.logger.info(
                                " ::: node exists in friends ( Numeric ID )--- changing to Target ::: "
                            )
                            self.graph.run(
                                "MATCH (n:Friend {numaric_id:'"
                                + t_id_numeric
                                + "',uid:"
                                + str(userid)
                                + "}) REMOVE n:Friend SET n:Target"
                            )
                            tnode = self.graph.run(
                                "Match (n:Target  {numaric_id:'"
                                + t_id_numeric
                                + "',uid:"
                                + str(userid)
                                + "}) return n"
                            )
                            tnode = tnode.data()
                            tnode[0]["n"]["id"] = t_id_numeric
                            tnode[0]["n"]["numaric_id"] = t_id_numeric
                            tnode[0]["n"]["creted_at"] = created_at
                            tnode[0]["n"]["picture_link"] = t_profile_pic_link
                            tnode[0]["n"].push()
                            return tnode

                    else:
                        self.logger.info(
                            " ::: node exists in friends--- changing to Target ::: "
                        )
                        self.graph.run(
                            "MATCH (n:Friend {id:'"
                            + t_id_numeric
                            + "',uid:"
                            + str(userid)
                            + "}) REMOVE n:Friend SET n:Target"
                        )
                        tnode = self.graph.run(
                            "Match (n:Target  {id:'"
                            + t_id_numeric
                            + "',uid:"
                            + str(userid)
                            + "}) return n"
                        )
                        tnode = tnode.data()
                        tnode[0]["n"]["id"] = t_id_numeric
                        tnode[0]["n"]["numaric_id"] = t_id_numeric
                        tnode[0]["n"]["creted_at"] = created_at
                        tnode[0]["n"]["picture_link"] = t_profile_pic_link
                        tnode[0]["n"].push()
                        return tnode

                else:
                    self.logger.info("node already exists -- numeric")
                    if t_id_numeric.isdigit():
                        pass
                    else:
                        tnode["n"]["id"] = t_id_numeric

                    if tnode["n"]["reference_number"]:
                        reference_number_list = tnode["n"]["reference_number"].split(
                            ","
                        ) + [reference_number]
                        reference_number_set = set(reference_number_list)
                        reference_number = reference_number_set.difference(
                            set(["", " "])
                        )
                        reference_number = ",".join(reference_number)

                    if tnode["n"]["case_number"]:
                        case_number_list = tnode["n"]["case_number"].split(",") + [
                            case_number
                        ]
                        case_number_set = set(case_number_list)
                        case_number = case_number_set.difference(set(["", " "]))
                        case_number = ",".join(case_number)
                    tnode["n"]["numaric_id"] = t_id_numeric
                    tnode["n"]["reference_number"] = reference_number
                    tnode["n"]["case_number"] = case_number
                    tnode["n"]["creted_at"] = created_at
                    tnode["n"]["picture_link"] = t_profile_pic_link
                    tnode["n"].push()

                ###End Here #####

            else:
                self.logger.info("Exists in friend node and changing it to target")
                self.graph.run(
                    "MATCH (n:Friend {id:'"
                    + t_id
                    + "',uid:"
                    + str(userid)
                    + "}) REMOVE n:Friend SET n:Target"
                )
                tnode = self.graph.run(
                    "Match (n:Target  {id:'"
                    + t_id
                    + "',uid:"
                    + str(userid)
                    + "}) return n"
                )
                tnode = tnode.data()
                tnode[0]["n"]["id"] = t_id_numeric
                tnode[0]["n"]["numaric_id"] = t_id_numeric
                tnode[0]["n"]["creted_at"] = created_at
                tnode[0]["n"]["picture_link"] = t_profile_pic_link
                tnode[0]["n"].push()
                return tnode
        else:
            self.logger.info("node already exists")
            if t_id.isdigit():
                pass
            else:
                tnode["n"]["id"] = t_id_numeric

            if tnode["n"]["reference_number"]:
                reference_number_list = tnode["n"]["reference_number"].split(",") + [
                    reference_number
                ]
                reference_number_set = set(reference_number_list)
                reference_number = reference_number_set.difference(set(["", " "]))
                reference_number = ",".join(reference_number)

            if tnode["n"]["case_number"]:
                case_number_list = tnode["n"]["case_number"].split(",") + [case_number]
                case_number_set = set(case_number_list)
                case_number = case_number_set.difference(set(["", " "]))
                case_number = ",".join(case_number)
            tnode["n"]["numaric_id"] = t_id_numeric
            tnode["n"]["reference_number"] = reference_number
            tnode["n"]["case_number"] = case_number
            tnode["n"]["creted_at"] = created_at
            tnode["n"]["picture_link"] = t_profile_pic_link
            tnode["n"].push()
        return tnode

    def create_friend_node(
        self,
        tnode,
        f_id,
        f_name,
        f_link,
        f_type,
        f_status_count,
        f_friend_count,
        f_follower_count,
        f_location,
        f_pic_link,
        rel_type,
        userid,
    ):
        """
        To create realtionship between the target and his friends
        """
        # fnode = self.graph.find_one('Target', 'id', str(f_id))
        fnode = None
        query = """
        Match (n:Target) where n.id={tid} and n.uid = {uid} return n
        """
        result = self.graph.run(
            query, parameters={"tid": str(f_id), "uid": int(userid)}
        )
        if result.forward() > 0:
            fnode = result.current()
            # print "friend found in in target"
        # else:
        #     print "Friend not found in Targets for userid " + userid
        if fnode is None:
            fnode = self.graph.find_one("Friend", "id", str(f_id))
            if fnode is None:
                fnode = Node(
                    "Friend",
                    id=str(f_id),
                    name=f_name,
                    profile=f_link,
                    type=f_type,
                    status_count=f_status_count,
                    friend_count=f_friend_count,
                    follower_count=f_follower_count,
                    location=f_location,
                    picture_link=f_pic_link,
                )
                self.graph.merge(fnode)
            else:
                self.logger.info("fnode exists already")

        if fnode is None:
            print("No Node to map")
            print("XXXXXXXXXXXXXXXXXXXXXXX")

        if rel_type == 0:
            relation = Relationship(tnode, "Friends_with", fnode)
            # self.logger.info("Relation : Friends_with")
        elif rel_type == 1:
            relation = Relationship(fnode, "Follows", tnode)
            # self.logger.info("Relation : Follows")
        elif rel_type == 2:
            relation = Relationship(tnode, "have video ", fnode)
            # self.logger.info("Relation : Follows")
        elif rel_type == 3:
            relation = Relationship(tnode, "commented on", fnode)
            # self.logger.info("Relation : Follows")
        self.graph.merge(relation)
        if len(f_location) > 0:
            self._location(fnode, f_location)
        return fnode

    def _location(self, node, location):
        if location != "":
            p_node = self.graph.find_one(
                "Location", "loc_lower", (location.lower()).strip()
            )
            if p_node is None:
                p_node = Node(
                    "Location", location=location, loc_lower=(location.lower()).strip()
                )
                self.graph.merge(p_node)
            relation = Relationship(node, "located_at", p_node)
            self.graph.merge(relation)

    def find_user_target(self, t_id, u_id):
        """
        To search for target with respective user
        """
        tnode = None
        query = """
        Match (n:Target) where n.id={tid} and n.uid = {uid} return n
        """
        result = self.graph.run(query, parameters={"tid": str(t_id), "uid": int(u_id)})
        if result.forward() > 0:
            tnode = result.current()
            print(" ::: Result tnode found :: ")
            print(" ### -------------------------------------- ###")
            print(tnode)
            print(" ### -------------------------------------- ###")
        else:
            print("No previous record " + str(t_id) + "userid " + str(u_id))
        return tnode

    def find_user_friend(self, t_id, u_id):
        """
        To search for target with respective user
        """
        tnode = None
        query = """
        Match (n:Friend {type:"1"}) where n.numaric_id={tid} and n.uid = {uid} return n
        """
        result = self.graph.run(query, parameters={"tid": str(t_id), "uid": int(u_id)})
        if result.forward() > 0:
            tnode = result.current()
            # print(" ### -------------------------------------- ###")
            # print (tnode)
            # print(" ### -------------------------------------- ###")
        else:
            print("No previous record " + str(t_id) + "userid " + str(u_id))
        return tnode

    def find_user_target_numeric(self, t_id, u_id):
        """This is a mystery - Why are you here ?"""

        """
            To search for target with respective user
        """
        tnode = None
        query = """
        Match (n:Friend) where n.numaric_id={tid} and n.uid = {uid} return n
        """
        result = self.graph.run(query, parameters={"tid": str(t_id), "uid": int(u_id)})
        if result.forward() > 0:
            tnode = result.current()
            # print (tnode)
        else:
            print("No previous record " + str(t_id) + "userid " + str(u_id))
        return tnode

    def find_user_target_without_userid(self, t_id):
        """
        To search for target with respective user
        """
        tnode = None
        query = """
        Match (n:Target) where n.id={tid} return n
        """
        result = self.graph.run(query, parameters={"tid": str(t_id)})
        if result.forward() > 0:
            tnode = result.current()
            # print tnode
        else:
            print("No previous record " + str(t_id) + "userid ")
        return tnode

    def get_target_followers(self, target_id):
        """
        Retrieve existing target followers
        :param target_id:
        :return:
        """
        query = """MATCH (n:Target{id:{t_id}})-[:Follows]-(b:Friend) RETURN b"""
        cursor = self.graph.run(query, parameters={"t_id": str(target_id)})
        followers_list = [dict(item[0]) for item in cursor]
        return followers_list

    def delete_node(self, tid):
        """
        To delete the existing node from neo4j
        """
        tnode = self.graph.find_one("Target", "id", str(tid))
        # query = """
        #     MATCH (n:Friend) WHERE NOT (n)-[]-(:Target) DETACH DELETE n
        # """
        if tnode is None:
            return
        query = """
        Match (n:Target) where n.id={tname} Detach Delete n
        """

        try:
            self.graph.run(query, parameters={"tname": tnode["id"]})
            self.logger.info("Node deleted")
        except Exception as identifier:
            self.logger.exception("Error" + identifier)
            # print identifier
            # print "query"
            # print "node deleted successfully"

    def _change_label_to_target(self, t_id):
        query = """
        Match (n:Friend) where n.id={fid} REMOVE n:Friend  SET n:Target
        """
        try:
            self.graph.run(query, parameters={"fid": str(t_id)})
            tnode = self.graph.find_one("Target", "id", str(t_id))
            self.logger.info("changed fnode to tnode")
            return tnode
        except Exception as identifier:
            # print identifier
            self.logger.error("Execution of changing Node failed :%s", identifier)
        return None

    def create_group_node(
        self, t_node, g_id, g_name, g_link, g_member, f_pic_link, userid
    ):
        """
        To create group node
        """
        if t_node is None:
            print("tnode is None")

        gnode = None
        query = """
        Match (n:Group) where n.id={g_id} and n.uid = {uid} return n
        """
        result = self.graph.run(
            query, parameters={"g_id": str(g_id), "uid": int(userid)}
        )
        if result.forward() > 0:
            gnode = result.current()
            # print "friend found in in target"
        # else:
        #     print "Friend not found in Targets for userid " + userid
        if gnode is None:
            gnode = Node(
                "Group",
                id=str(g_id),
                name=g_name,
                profile=g_link,
                g_member=g_member,
                picture_link=f_pic_link,
                uid=int(userid),
            )
            print("group node created")
        relation = Relationship(t_node, "member of", gnode)
        # self.logger.info("Relation : Friends_with")
        self.graph.merge(relation)
        print("relationship made")

    def create_likes_node(
        self, t_node, p_id, p_name, p_link, p_type, p_pic_link, userid
    ):
        """
        To create page node
        """
        pnode = None
        query = """
        Match (n:Pages) where n.id={p_id} and n.uid = {uid} return n
        """
        result = self.graph.run(
            query, parameters={"p_id": str(p_id), "uid": int(userid)}
        )
        if result.forward() > 0:
            print("page node exists     " + p_name)
            pnode = result.current()
        else:
            pnode = Node(
                "Pages",
                id=str(p_id),
                name=p_name,
                profile=p_link,
                page_type=p_type,
                picture_link=p_pic_link,
                uid=int(userid),
            )
            print("page node created    " + p_name)
        relation = Relationship(t_node, "likes", pnode)
        self.graph.merge(relation)
        print("relationship made")

    def create_checkins_node(self, t_node, c_name, c_link, c_pic, userid):
        """
        To create checkins node
        """
        cnode = None
        query = """
            Match (n:Checkins) where n.name={c_name} and n.uid = {uid} return n
            """
        result = self.graph.run(
            query, parameters={"c_name": str(c_name), "uid": int(userid)}
        )
        if result.forward() > 0:
            print("checkins node exists" + c_name)
            cnode = result.current()
        else:
            cnode = Node(
                "Checkins",
                name=c_name,
                profile=c_link,
                picture_link=c_pic,
                uid=int(userid),
            )
            print("checkins node created:   " + c_name)
        relation = Relationship(t_node, "checks in", cnode)
        self.graph.merge(relation)
        print("relationship made")

    def create_channel_node(
        self,
        c_id,
        c_name,
        c_link,
        t_status_count,
        t_friend_count,
        t_follower_count,
        t_profile_pic_link,
        userid,
    ):
        """
        To create nodes of the data available
        """
        # TODO cyper query to find target with crossponding user
        cnode = self.find_user_target(c_id, userid)
        if cnode is None:
            cnode = Node(
                "Channel",
                c_id=c_id,
                c_name=c_name,
                c_link=c_link,
                t_status_count=t_status_count,
                t_friend_count=t_friend_count,
                t_follower_count=t_follower_count,
                t_profile_pic_link=t_profile_pic_link,
                uid=int(userid),
            )
            print("Channel node created node created    " + c_name)
        else:
            self.logger.info("node already exists")
        return cnode

    def create_city_node(self, t_node, name):
        citynode = None
        query = """
        Match (n:City) where n.name={name} return n
        """
        result = self.graph.run(query, parameters={"name": str(name)})
        if result.forward() > 0:
            print("city node exists" + name)
            cnode = result.current()
        else:
            cnode = Node("City", name=name)
            print("City node created" + name)
        relation = Relationship(t_node, "lives in", cnode)
        self.graph.merge(relation)
        print("city relationship made")

    def create_education_node(self, t_node, e_id, e_name):
        education_node = None
        query = """
        Match (n:Education) where n.id={id} return n
        """
        result = self.graph.run(query, parameters={"id": str(e_id)})
        if result.forward() > 0:
            print("Education node exists" + e_name)
            education_node = result.current()
        else:
            education_node = Node("Education", id=e_id, name=e_name)
            print("Education node created" + e_name)
        relation = Relationship(t_node, "Study at", education_node)
        self.graph.merge(relation)
        print("Education relationship made")

    def create_work_node(self, t_node, w_id, w_name):
        work_node = None
        query = """
        Match (n:Work) where n.id={id} return n
        """
        result = self.graph.run(query, parameters={"id": str(w_id)})
        if result.forward() > 0:
            print("work node exists " + w_name)
            work_node = result.current()
        else:
            work_node = Node("Work", id=w_id, name=w_name)
            print("Work node created    " + w_name)
        relation = Relationship(t_node, "work at", work_node)
        self.graph.merge(relation)
        print("Work relationship made")

    def convertstring(self, fulljson, name):
        if name == "checkins":
            final_string = "["
            s = Template('{ name : "$name" , link : "$link" , image : "$image"}')
            for x in fulljson:
                image = x["image"]
                link = x["link"]
                name = x["name"]
                t = s.substitute(name=name, link=link, image=image)
                final_string = final_string + t + ","
            final_string = final_string[:-1] + "]"
            return final_string
        elif name == "likes":
            final_string = "["
            s = Template(
                '{ name : "$name" , link : "$link" , image : "$image" , type : "$l_type"}'
            )
            for x in fulljson:
                image = x["image"]
                link = x["link"]
                name = x["name"]
                l_type = x["type"]
                t = s.substitute(name=name, link=link, image=image, l_type=l_type)
                final_string = final_string + t + ","
            final_string = final_string[:-1] + "]"
            return final_string
        elif name == "groups":
            final_string = "["
            s = Template(
                '{ id : "$id" ,name : "$name" , profile : "$link", picture_link : "$image"}'
            )
            for x in fulljson:
                id = x["id"]
                image = x["image_link"]
                link = x["link"]
                name = x["name"]
                t = s.substitute(id=id, name=name, link=link, image=image)
                final_string = final_string + t + ","
            final_string = final_string[:-1] + "]"
            return final_string
            # return final_string.decode('unicode-escape')
        elif name == "friends":
            final_string = "["

            s = Template(
                '{id : "$f_id",f_numaric_id:"$num_id", name : "$f_name", profile : "$f_link", type: "1" , status_count : "0", friend_count : "0", follower_count: "0", location:"", picture_link:"$f_pic" , city :"$city" , edu :"$edu" , work :"$work", cityn :[$cityn] , edun :[$edun] , workn :[$workn]}'
            )
            for x in fulljson:
                f_id = x.get("id", "")
                f_num_id = x.get("numaric_id", "")
                f_link = x.get("profile", "")
                f_name = x.get("name", "")
                f_pic = x.get("picture_link", "")
                f_city = x.get("cityn", "")
                f_work = x.get("workn", "")
                f_edu = x.get("edun", "")
                cityp = x.get("city", "")
                workp = x.get("work", "")
                edup = x.get("edu", "")
                city = work = edu = ""
                if f_city:
                    city_template = Template('{name : "$city_name"}')
                    city = city_template.substitute(city_name=f_city[0])
                if f_work:
                    for each in f_work:
                        work_template = Template('{id : "$w_id" , name : "$w_name"}')
                        work = (
                            work_template.substitute(
                                w_id=each["id"], w_name=each["name"]
                            )
                            + ","
                            + work
                        )
                    work = work[:-1]
                if f_edu:
                    for each in f_edu:
                        edu_template = Template('{id : "$e_id" , name : "$e_name"}')
                        edu = (
                            edu_template.substitute(
                                e_id=each["id"], e_name=each["name"]
                            )
                            + ","
                            + edu
                        )
                    edu = edu[:-1]
                t = s.substitute(
                    f_id=f_id,
                    num_id=f_num_id,
                    f_name=f_name,
                    f_link=f_link,
                    f_pic=f_pic,
                    city=cityp,
                    edu=edup,
                    work=workp,
                    cityn=city,
                    edun=edu,
                    workn=work,
                )
                final_string = final_string + t + ","
            final_string = final_string[:-1] + "]"
            return final_string

    def create_batch_checkins(self, node, all_json):
        try:
            id = node.data()["n"].get("id")
            uid = node.data()["n"].get("uid")
        except:
            if isinstance(node, list):
                id = node[0]["n"]["id"]
                uid = node[0]["n"]["uid"]
            else:
                id = node.get("id")
                uid = node.get("uid")
        l = self.convertstring(all_json, name="checkins")
        q = (
            """UNWIND [{id: '"""
            + id
            + """' , uid : toInt('"""
            + str(uid)
            + """')}] as user 
            UNWIND """
            + l
            + """ as c 
            MERGE (u:Target {id: user.id , uid : user.uid}) 
            MERGE (y:Checkins {name: c.name , link :c.link , picture_link:c.image, uid : user.uid}) 
            MERGE (u)-[:`checks in`]->(y)"""
        )
        tx = self.graph.begin()
        tx.run(q)
        self.logger.info("Commiting transaction")
        tx.commit()
        self.logger.info("transaction Commited")

    def create_batch_likes(self, node, all_json):
        try:
            id = node.data()["n"].get("id")
            uid = node.data()["n"].get("uid")
        except:
            if isinstance(node, list):
                id = node[0]["n"]["id"]
                uid = node[0]["n"]["uid"]
            else:
                id = node.get("id")
                uid = node.get("uid")
        l = self.convertstring(all_json, name="likes")
        q = (
            """UNWIND [{id: '"""
            + id
            + """' , uid : toInt('"""
            + str(uid)
            + """')}] as user 
            UNWIND """
            + l
            + """ as c 
            MERGE (u:Target {id: user.id , uid : user.uid}) 
            MERGE (y:Pages {name: c.name , link :c.link , picture_link:c.image , type:c.type, uid : user.uid}) 
            MERGE (u)-[:`likes`]->(y)"""
        )
        tx = self.graph.begin()
        tx.run(q)
        self.logger.info("Commiting transaction")
        tx.commit()
        self.logger.info("transaction Commited")

    def create_batch_groups(self, node, all_json):
        try:
            id = node.data()["n"].get("id")
            uid = node.data()["n"].get("uid")
        except:
            if isinstance(node, list):
                id = node[0]["n"]["id"]
                uid = node[0]["n"]["uid"]
            else:
                id = node.get("id")
                uid = node.get("uid")
        l = self.convertstring(all_json, name="groups")
        q = (
            """UNWIND [{id: '"""
            + id
            + """' , uid : toInt('"""
            + str(uid)
            + """')}] as user 
            UNWIND """
            + l
            + """ as c 
            MERGE (u:Target {id: user.id , uid : user.uid}) 
            MERGE (y:Group {id: c.id , name: c.name , link :c.profile , picture_link:c.picture_link, uid : user.uid }) 
            MERGE (u)-[:`member of`]->(y)"""
        )
        tx = self.graph.begin()
        tx.run(q)
        self.logger.info("Commiting transaction")
        tx.commit()
        self.logger.info("transaction Commited")

    def get_friends_count(self, node, label="Target", relation="Friends_with"):
        tnode = None
        try:
            id = node.data()["n"].get("id")
            uid = node.data()["n"].get("uid")
        except:
            if isinstance(node, list):
                id = node[0]["n"]["id"]
                uid = node[0]["n"]["uid"]
            else:
                id = node.get("id")
                uid = node.get("uid")
        query = (
            """MATCH (a:Target {id: '"""
            + id
            + """', uid:toInt('"""
            + str(uid)
            + """')})-[r:`"""
            + relation
            + """`]-(b) return count(b) """
        )
        result = self.graph.run(query)
        if result.forward() > 0:
            tnode = result.current()
            return tnode[0]
        else:
            print("No previous record " + str(t_id) + "userid " + str(u_id))
        return tnode

    def filter_friends(self, l, uid):
        ### Checks if a node exists on the basis of numeric id;
        ### if exist then update the id of node to numeeric id ###

        # for x in all_json:
        #     f_id = x.get("id",'')
        #     f_num_id = x.get('numaric_id','')
        #     if f_num_id:
        #         tnode = self.find_user_friend(f_num_id, uid)
        #         if tnode is not None:
        #             #### Update id to numeric id #####
        #             if tnode['n']['id'].isdigit():
        #                 pass
        #             else:
        #                 tnode['n']['id'] = f_num_id
        #                 tnode['n'].push()

        # query_all = """
        #     UNWIND """+ l +""" as c
        #     Match (n:Friend {numaric_id : c.f_numaric_id , uid : toInt('""" + str(uid) + """'), type:"1"})
        #     SET n.id = c.f_numaric_id
        # """

        # query = """
        #     UNWIND $inputArray AS c
        #     Match (n:Friend {numaric_id : c.numaric_id , uid : toInt('""" + str(uid) + """'), type:"1"})
        #                 SET n.id = c.numaric_id
        # """

        query = """
            UNWIND $inputArray AS c
            Match (n:Friend) where n.numaric_id = c.numaric_id and n.uid = {uid} and n.type="1"
            SET n.id = c.numaric_id
        """

        self.logger.info("Commiting transaction-Updating ids to numeric ids")
        self.graph.run(query, parameters={"inputArray": l, "uid": int(uid)})
        # self.graph.run(query, parameters={'inputArray': l})
        print("transaction Commited-ids updated to numeric")

    def create_batch_friends(
        self, node, all_json, label="Target", relation="Friends_with"
    ):
        try:
            id = node.data()["n"].get("id")
            uid = node.data()["n"].get("uid")
        except:
            #    id = node.get("id")
            #    uid = node.get("uid")
            if isinstance(node, list):
                id = node[0]["n"]["id"]
                uid = node[0]["n"]["uid"]
            else:
                id = node.get("id")
                uid = node.get("uid")
        l = self.convertstring(all_json, name="friends")
        if str(uid) == "7":
            self.filter_friends(all_json, str(uid))
        q = (
            """UNWIND [{id: '"""
            + id
            + """' , uid : toInt('"""
            + str(uid)
            + """')}] as user
            UNWIND """
            + l
            + """ as c
            OPTIONAL MATCH (n:Target {id : c.id , uid : toInt('"""
            + str(uid)
            + """'),type:"1"})
            OPTIONAL MATCH (m:Friend {numaric_id : c.f_numaric_id , uid : toInt('"""
            + str(uid)
            + """'),type:"1"})
            WITH coalesce(n, m) as node,user,c // returns first non-null value
            CALL apoc.do.when(node is null, "MERGE (n:Friend {id:c.id,numaric_id:c.f_numaric_id,uid:user.uid,name:c.name,city:c.city,edu:c.edu,work:c.work,profile: c.profile,type:'1',status_count:'0',friend_count:'0',follower_count:'0',location:'',picture_link:c.picture_link}) RETURN n", '', {c:c,user:user}) YIELD value
            with coalesce(node, value.n) as y,user,c
            MERGE (u:"""
            + label
            + """ {id: user.id , uid : user.uid})
            MERGE (u)-[:`"""
            + relation
            + """`]->(y)
            foreach (sc in c.cityn | merge(cn:City {name:sc.name, uid : user.uid}) merge (y)-[:`lives in`]-(cn))
            foreach (sw in c.workn | merge(wn:Work {id:sw.id , name:sw.name, uid : user.uid}) merge (y)-[:`work at`]-(wn))
            foreach (se in c.edun | merge(en:Education {id:se.id , name:se.name, uid : user.uid}) merge (y)-[:`Study at`]-(en))
            """
        )
        try:
            from datetime import datetime

            dd = str(datetime.now().time())
            dd = dd.replace(":", "").replace(".", "")
            self.logger.info("transactions stored")
            with open("transactions/" + id + dd + ".txt", "w", encoding="utf-8") as f:
                f.write(q)
        except Exception as ex:
            print(ex)
            self.logger.info("transactions stored error")

        tx = self.graph.begin()
        tx.run(q)
        self.logger.info("Commiting transaction")
        print("Commiting transaction")
        tx.commit()
        self.logger.info("transaction Commited")
        print("transaction Commited")

    def create_batch_friends_activity(
        self,
        node,
        all_json,
        friends_status,
        label="Target",
        relation="Friends_with",
        activity="activity_p",
    ):
        try:
            id = node.data()["n"].get("id")
            uid = node.data()["n"].get("uid")
        except:
            #    id = node.get("id")
            #    uid = node.get("uid")
            if isinstance(node, list):
                id = node[0]["n"]["id"]
                uid = node[0]["n"]["uid"]
            else:
                id = node.get("id")
                uid = node.get("uid")
        l = self.convertstring(all_json, name="friends")
        if str(uid) == "7":
            self.filter_friends(all_json, str(uid))
        if friends_status == "public":
            final_relation = """MERGE (u)-[:`""" + activity + """`]->(y)"""

        if friends_status == "private":
            final_relation = (
                """MERGE (u)-[:`"""
                + relation
                + """`]->(y)
                                MERGE (u)-[:`"""
                + activity
                + """`]->(y)"""
            )

        q = (
            """UNWIND [{id: '"""
            + id
            + """' , uid : toInt('"""
            + str(uid)
            + """')}] as user
            UNWIND """
            + l
            + """ as c
            OPTIONAL MATCH (n:Target {id : c.id , uid : toInt('"""
            + str(uid)
            + """'), type:"1"})
            OPTIONAL MATCH (m:Friend {numaric_id : c.f_numaric_id , uid : toInt('"""
            + str(uid)
            + """'), type:"1"})
            WITH coalesce(n, m) as node,user,c // returns first non-null value
            CALL apoc.do.when(node is null, "MERGE (n:Friend {id:c.id,numaric_id:c.f_numaric_id,uid:user.uid,name:c.name,city:c.city,edu:c.edu,work:c.work,profile: c.profile,type:'1',status_count:'0',friend_count:'0',follower_count:'0',location:'',picture_link:c.picture_link}) RETURN n", '', {c:c,user:user}) YIELD value
            with coalesce(node, value.n) as y,user,c
            MERGE (u:"""
            + label
            + """ {id: user.id , uid : user.uid})
            """
            + final_relation
            + """
            foreach (sc in c.cityn | merge(cn:City {name:sc.name, uid : user.uid}) merge (y)-[:`lives in`]-(cn))
            foreach (sw in c.workn | merge(wn:Work {id:sw.id , name:sw.name, uid : user.uid}) merge (y)-[:`work at`]-(wn))
            foreach (se in c.edun | merge(en:Education {id:se.id , name:se.name, uid : user.uid}) merge (y)-[:`Study at`]-(en))
            """
        )
        try:
            from datetime import datetime

            dd = str(datetime.now().time())
            dd = dd.replace(":", "").replace(".", "")
            with open("transactions/" + id + dd + ".txt", "w", encoding="utf-8") as f:
                f.write(q)
            self.logger.info("transactions stored")
        except Exception as ex:
            print(ex)
            self.logger.info("transactions stored error")
        tx = self.graph.begin()
        tx.run(q)
        self.logger.info("Commiting transaction")
        print("Commiting transaction")
        tx.commit()
        self.logger.info("transaction Commited")
        print("transaction Commited")

    def create_or_get_group_node(
        self, g_id, g_name, g_link, g_member, f_pic_link, userid
    ):
        """
        To create or get group node
        """
        gnode = None
        query = """
        Match (n:Group) where n.id={g_id} and n.uid = {uid} return n
        """
        result = self.graph.run(
            query, parameters={"g_id": str(g_id), "uid": int(userid)}
        )
        if result.forward() > 0:
            gnode = result.current()
            print("group node found")
        if gnode is None:
            gnode = Node(
                "Group",
                id=str(g_id),
                name=g_name,
                profile=g_link,
                g_member=g_member,
                picture_link=f_pic_link,
                uid=int(userid),
            )
            print("group node created")
            self.graph.merge(gnode)
        return gnode

    def delete_duplicates(self, user_id):
        try:
            query = (
                """ MATCH (p:Friend {uid:"""
                + user_id
                + """, type:'1'} )
                    WITH p.id as id, collect(p) AS nodes
                    WHERE size(nodes) >  1
                    FOREACH (g in tail(nodes) | detach DELETE g) """
            )
            self.graph.run(query)
            self.logger.info("removing dublicates Friend executed")
            query = (
                """ MATCH (p:Target {uid:"""
                + user_id
                + """, type:'1'} )
                    WITH p.id as id, collect(p) AS nodes
                    WHERE size(nodes) >  1
                    FOREACH (g in tail(nodes) | detach DELETE g) """
            )
            self.graph.run(query)
            self.logger.info("removing dublicates Target executed")

            if user_id != "7":
                # import pdb; pdb.set_trace()
                query = (
                    """ MATCH (p:Friend {uid:"""
                    + user_id
                    + """, type:'1'})
                    WITH p.numaric_id as id, collect(p) AS nodes
                    WHERE size(nodes) >  1
                    FOREACH (g in tail(nodes) | detach DELETE g) """
                )
                self.graph.run(query)
                self.logger.info("removing dublicates Friends(Numeric) executed")

        except Exception as ex:
            print(ex)
            self.logger.info("ex")
