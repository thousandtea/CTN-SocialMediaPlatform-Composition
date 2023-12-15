from flask import Flask, request, jsonify
import graphene

app = Flask(__name__)


class User(graphene.ObjectType):
    id = graphene.ID()
    name = graphene.String()
    email = graphene.String()


# define GraphQL Schema
class Query(graphene.ObjectType):
    hello = graphene.String(description='A typical hello world')
    user = graphene.Field(User)

    def resolve_hello(self, info):
        return 'Hello, world!'

    def resolve_user(self, info):
        return User(id="1", name="Chang Liu", email="cl4404@columbia.edu")


schema = graphene.Schema(query=Query)


@app.route("/api/graphql", methods=["GET"])
def graphql_api():
    # query from post
    query = request.args.get("query")

    # execute query
    result = schema.execute(query)

    # return response
    return jsonify(result.data)


if __name__ == '__main__':
    app.run(debug=True)
