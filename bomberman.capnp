@0xb61678a79b98b42e;

interface Login {
    connect @0 (client :Client, name :Text) -> (server :Server, handle :LoginHandle);

    interface LoginHandle {}
}

struct Command {
    name @0 :Text;
    args @1 :List(Text);
}

interface Client {
    send @0 (command :Command);
}

interface Server {
    join @0 () -> (character :Character);
    send @1 (command :Command);
}

interface Character {
    do @0 (action :Text);
}
