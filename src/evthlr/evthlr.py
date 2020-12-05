class Event:
    def __init__(self):
        self._observers = []
    
    def register_observer(self, observer):
        self._observers.append(observer)

    def trigger_event(self, *kwargs, **args):
        meme = args
        meme2 = kwargs
        for observer in self._observers:
            observer.upon_trigger(self, *meme2, **meme)

class Observer:
    def __init__(self, observable):
        observable.register_observer(self)

    def upon_trigger(self, observable, *args, **kwargs):
        print('Got', *args, *kwargs.values(), 'From', observable)


"""
## Test Code, example of how an observer would be inherited

class GestureRecognizer(Observer):
    def __init__(self, event):
        event.register_observer(self)

    def response(self, *args, **kwargs):
        print('Haha I see u silly gesture')
        # do some ML shit to know gesture
        pass

    # def upon_trigger(self, observable, *args, **kwargs):
    #     Observer.upon_trigger(self, observable, *args, **kwargs)
    #     self.response(*args, **kwargs)
        
subject = Event()
recon = GestureRecognizer(subject)
subject.trigger_event('test')

## this prints out: 
## Got test From <address>
## Haha I see u silly gesture

"""




 